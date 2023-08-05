from vayaAuto import __BASE__
import sys
import configparser
import time
import copy
import yaml
import threading
from yaml.loader import SafeLoader
import logging
from subprocess import Popen, PIPE, STDOUT
from vayaAuto.section import Section
import os
logger = logging.getLogger()


def osPath(func):
    def wrapper(*args, **kwargs):

        if os.name == 'nt':
            osArgs = []
            for i, arg in enumerate(args):
                if isinstance(arg, str):
                    osArg = os.sep.join(arg.split('/'))
                    osArgs.append(osArg)
                else:
                    osArgs.append(arg)
            func(*tuple(osArgs), **kwargs)
        else:
            func(*tuple(args), **kwargs)
    return wrapper


class VayaDrive(object):
    VD, VDCONSOLE = 0, 1

    @osPath
    def __init__(self, vaya_dir_path, console=False):
        self.process_output = []
        self.temp_ini_file_path = os.path.join(__BASE__, 'temp.ini')
        self.local_ini_path = os.path.join(os.path.dirname(vaya_dir_path), 'local.ini')
        self.vaya_dir_path = vaya_dir_path
        self.log_catcher_thread = None
        self.timeout_thread = None
        self.version = None
        self.is_paused = False
        self.ignore_list = []
        self.compiled = False
        self.configuration = {}
        self.b_configuration = {}
        self.exe_path = None
        self.default_config_folder = os.path.join(vaya_dir_path, 'DefaultConfigs')
        self.default_config_paths = {}
        self.parent_dir = os.path.abspath(os.path.join(vaya_dir_path, os.pardir))
        self._seq_output_folder = ''
        self._consoleMode = 0
        self.vayadrive_process = None
        if os.path.isdir(self.default_config_folder):
            self.gather_default_configs(self.default_config_folder)
        else:
            logger.info(f'not found default config folder in {self.default_config_folder}')
        self.consoleMode = str(console).lower()
        self.engine_logs = []
        self.set_vaya_config()
        self.generate_properties()

    def generate_properties(self):
        here = os.path.dirname(os.path.abspath(__file__))
        with open(f'{here}/configurations/vayadrive_params.yaml') as f:
            data = yaml.load(f, Loader=SafeLoader)
            for sec, options in data.items():
                for attr_name, option in options.items():
                    # setattr(VayaDrive, attr_name, None)
                    try:
                        if not hasattr(self, attr_name):
                            setattr(VayaDrive, attr_name, property(self.get_func(sec, option),
                                                                   self.set_func(sec, option)))
                    except KeyError as e:
                        logger.info(f'Unable to set attribute {attr_name}')

    # """
    # create GLOBAL TAB get and set functions
    # """
    def get_func(self, section, option):
        def getf(self):
            try:
                return self.configuration[section][option].value
            except KeyError as e:
                return ''
        return getf

    def set_func(self, section, option):
        def setf(self, value):
            self.set_explicit_param(section=section, option=option, value=value)
        return setf

    @property
    def seq_output_folder(self):
        return self._seq_output_folder

    @seq_output_folder.setter
    def seq_output_folder(self, value):
        self._seq_output_folder = value

    @property
    def consoleMode(self):
        return self._consoleMode

    @consoleMode.setter
    def consoleMode(self, value):

        if str(value).lower() == 'true':
            self._consoleMode = self.VDCONSOLE
        else:
            self._consoleMode = self.VD
        logger.info(f'vayadrive console mode = {self._consoleMode}')
        self.set_exe_path(self.vaya_dir_path)

    # @osPath
    def record_mode(self, calib_folder, output_folder):
        self.runningMode = '7'
        self.createFrames = 'false'
        self.recordToDisk = 'true'
        self.defaultCalibFolderString = calib_folder
        self.recordLocationString = output_folder

    # @osPath
    def live_mode(self, calib_folder, output_folder):
        self.runningMode = '7'
        self.createFrames = 'true'
        self.recordToDisk = 'false'
        self.defaultCalibFolderString = calib_folder
        self.recordLocationString = output_folder

    def playback_mode(self):
        self.runningMode = '5'

    def gather_default_configs(self, default_config):

        for file in os.listdir(default_config):
            file_path = os.path.join(default_config, file)
            if os.path.isdir(file_path):
                self.gather_default_configs(file_path)
            elif file.endswith(r'.ini'):
                self.default_config_paths[os.path.splitext(file)[0]] = file_path

    def set_explicit_param(self, **kwargs):
        sec = kwargs.pop('section')
        option = kwargs.pop('option')
        value = kwargs.pop('value')
        if sec not in self.configuration.keys():
            section = Section(sec)
            self.configuration[sec] = section
        if option not in self.configuration[sec].keys():
            self.configuration[sec].add_option(option)
        self.configuration[sec][option].value = str(value)

    # @osPath
    def find_vd_exe_path(self, path, posix):
        for (root, dirs, files) in os.walk(path, topdown=True):
            if self.consoleMode and f"VayaDriveConsole{posix}" in files:
                return root
            elif not self.consoleMode and f'VayaDrive{posix}' in files:
                return root
        else:
            logger.error('not found EXE path')
            raise VayaException(f"couldn't find VayaDrive exe file")

    # @osPath
    def set_exe_path(self, path):
        if os.name == 'nt':
            posix = '.exe'
            build_folder = 'build_vs2019'
        else:
            posix = ''
            build_folder = 'build_Release'
        if os.path.isdir(os.path.join(path, 'Release')):
            path = os.path.join(path, 'Release')
        elif os.path.isdir(os.path.join(path, build_folder)):
            path = os.path.join(path, build_folder, 'Release')
        else:
            path = self.find_vd_exe_path(path, posix)
            self.compiled = True
        if self.consoleMode:
            self.exe_path = os.path.join(path, f'VayaDriveConsole{posix}')
        else:
            self.exe_path = os.path.join(path, f"VayaDrive{posix}")
        logger.info(f'found exe - {self.exe_path}')
        logger.info(f'compiled version = {self.compiled}')

    def set_vaya_config(self):
        if self.configuration:
            self.configuration = {}
        # self.delete_temp_ini()
        self.run_vayadrive(nogui=True, export_full_ini=True, autostart=True)
        config = configparser.ConfigParser()
        config.optionxform = str
        with open(self.temp_ini_file_path, "r") as f:
            lines = f.readlines()
            if len(lines) == 0:
                raise VayaException(f'Unable to dump full config using -d \n'
                                    f'-----PROCESS OUTPUT-----\n'
                                    f'{self.vayadrive_process.stdout.readlines()}\n'
                                    f'{self.process_output}')
        with open(self.temp_ini_file_path, "w") as f:
            for line in lines:
                if any([word in line for word in ['DefaultValue','Units', ' ', '%']]):
                    continue
                else:
                    f.write(line)

        config.read(self.temp_ini_file_path)
        for sec in config.sections():

            section = Section(sec)
            for option in config[sec]:
                section.add_option(option)
                try:
                    section[option].value = config.get(sec, option)
                except Exception as e:
                    raise VayaException(f'Get an exception \n{e}')
                self.configuration[sec] = section

        self.b_configuration = copy.deepcopy(self.configuration)

    @osPath
    def set_configuration_with_ini(self, ini_path, reset=False):
        if reset:
            self.reset()
        config = configparser.ConfigParser()
        config.optionxform = str
        config.read(ini_path)
        for sec in config.sections():
            for option in config[sec]:
                if sec not in self.configuration.keys():
                    section = Section(sec)
                    self.configuration[sec] = section
                if option not in self.configuration[sec].keys():
                    self.configuration[sec].add_option(option)
                self.configuration[sec][option].value = config.get(sec, option)

    def export_ini_file(self):

        config = configparser.ConfigParser()
        config.optionxform = str
        for name, sec in self.configuration.items():
            config[name] = sec
            # config[name] = {}
            # for option_name, option in sec.items():
            #     if option.value is None:
            #         continue
            #     # print(f'insert value to ini file\nsection: {sec}\noption: {option} value: {str(option.value)}\n-------------------')
            #     config[name][option_name] = str(option.value)
        # self.ini_path = os.path.join(self.vaya_dir_path, 'override.ini')
        with open(self.temp_ini_file_path, 'w') as configfile:
            config.write(configfile)
        self.update_local_ini()

    def create_local_ini(self):

        config = configparser.ConfigParser()
        config.optionxform = str
        output_location = self.outputLocation
        record_location = self.recordLocationString
        default_calib_folder = self.defaultCalibFolderString
        config['Global'] = {'OutputLocation': output_location}
        config['Reader-Sensors'] = {'RECORD_LOCATION_String': record_location,
                                    'DEFAULT_CALIB_FOLDER_String': default_calib_folder}
        with open(self.local_ini_path, 'w') as local_ini:
            config.write(local_ini)

    def update_local_ini(self):
        config = configparser.ConfigParser()
        config.optionxform = str
        try:
            output_location = self.outputLocation
            record_location = self.recordLocationString
            default_calib_folder = self.defaultCalibFolderString
        except AttributeError:
            output_location = ''
            record_location = ''
            default_calib_folder = ''
        config['Global'] = {'OutputLocation': output_location}
        config['Reader-Sensors'] = {'RECORD_LOCATION_String': record_location,
                                    'DEFAULT_CALIB_FOLDER_String': default_calib_folder}
        with open(self.local_ini_path, 'w') as local_ini:
            config.write(local_ini)


    def run_vayadrive(self, nogui=False, autostart=False, get_process=False, export_full_ini=False, force_run=False,
                      qt=False, preset=False, o_params=None, non_blocking_mode=False, timeout=0):
        if o_params is None:
            o_params = []
        self.seq_output_folder = ''
        self.export_ini_file()
        call_list = [self.exe_path]
        if nogui:
            call_list.append('-nogui')
        if autostart:
            call_list.append('-autostart')
        if preset:
            call_list.append(f'-p{self.temp_ini_file_path}')
        else:
            call_list.append(f'-c{self.temp_ini_file_path}')
        if o_params:
            call_list += o_params
        if export_full_ini:
            call_list.append(f'-d')

        env = dict(os.environ)
        if not self.compiled:
            if os.name == 'posix':  # LINUX
                dependencies = self.extract_dependencies_linux()
                dependencies = dependencies
                try:
                    ld_library_path = env['LD_LIBRARY_PATH']
                    env['LD_LIBRARY_PATH'] = dependencies + ld_library_path
                except:
                    env['LD_LIBRARY_PATH'] = dependencies
            elif os.name == 'nt':  # WINDOWS
                dependencies = self.extract_dependencies_windows()
                win_path = env['PATH']
                env['PATH'] = dependencies + win_path
        if qt:
            return {'call_list': call_list, 'env': env, 'cwd': self.vaya_dir_path}
        self.vayadrive_process = Popen(call_list, cwd=self.vaya_dir_path, env=env,  stdout=PIPE, stderr=STDOUT)
        if get_process and not non_blocking_mode:
            return self.vayadrive_process
        if non_blocking_mode:
            self.log_catcher_thread = threading.Thread(target=self.catch_log, args=(export_full_ini, force_run))
            self.log_catcher_thread.start()
            if get_process:
                return self.vayadrive_process
        else:
            if timeout:
                self.timeout_thread = threading.Thread(target=self.timeout_handler, args=(timeout, ))
                self.timeout_thread.start()
            self.catch_log(export_full_ini, force_run)

    def catch_log(self, export_full_ini, force_run):
        self.process_output = []
        while self.vayadrive_process.poll() is None:
            output = self.vayadrive_process.stdout.readline().decode('utf-8')
            self.process_output.append(output)
            # sys.stdout.write(output)
            if 'ERROR' in output and not force_run:
                if self.check_ignore_list(output):
                    continue
                self.vayadrive_process.kill()
                if not export_full_ini:
                    raise VayaException(f'Found error in VD log\n{output}')
            if 'Loading engine' in output:
                self.engine_logs.append(output)
            if 'Output folder created:' in output:
                self.seq_output_folder = output.split()[-1]
            if 'Pause: 1' in output:
                self.is_paused = True
            elif 'Pause: 0' in output:
                self.is_paused = False
            if not self.version and 'Version' in output:
                output = output.replace('\r', '')
                output = output.replace('\n', '')
                self.version = output.split('Version: ')[-1]

    def check_ignore_list(self, log_error) -> bool:
        for ignored_error in self.ignore_list:
            if ignored_error in log_error:
                return True
        return False

    def timeout_handler(self, timeout):
        target_timeout = time.time() + timeout
        while time.time() <= target_timeout:
            pass
        self.vayadrive_process.kill()

    def enabled_cameras(self):
        for name, option in self.configuration['Pipe-0'].items():
            if 'SensorEnable_CAMERA' in name and option.value == 'true':
                yield option.name.split('_')[2]

    def enabled_radars(self):
        for name, option in self.configuration['Pipe-0'].items():
            if 'SensorEnable_Radar' in name and option.value == 'true':
                yield option.name.split('_')[2]

    def enabled_lidars(self):
        for name, option in self.configuration['Pipe-0'].items():
            if 'SensorEnable_LIDAR' in name and option.value == 'true':
                yield option.name.split('_')[2]

    def delete_temp_ini(self):
        if os.path.isfile(self.temp_ini_file_path):
            os.remove(self.temp_ini_file_path)

    def extract_dependencies_linux(self):
        run_sh = os.path.join(self.vaya_dir_path, 'cmake_vv_scripts', 'cmake_run_release.sh')
        depends = ''
        with open(run_sh, 'r') as f:
            lines = f.readlines()
            for line in lines:
                if 'EXPORT' in line and line.index('EXPORT') == 0:
                    depends += line.split('=')[1][:-1] + ':'
        depends += f'../Libs/PCL/PCL-1.8.1/lib/ubuntu1804:'
        return depends + f'../Libs/PCL/PCL-1.8.1/lib/ubuntu1804:'

    def extract_dependencies_windows(self):
        run_bat = os.path.join(self.vaya_dir_path, 'cmake_run_vs2019.bat')
        with open(run_bat, 'r') as f:
            lines = f.readlines()
            for line in lines:
                if 'PATH' in line:
                    return line[9:-7]
        return False

    def turn_off_all_algos(self, pipe: int):
        for key, val in self.configuration[f'Pipe-{pipe}'].items():
            if key.endswith('Bool') and not any(map(key.__contains__, ['Settings', 'SensorEnable'])):
                val.value = 'false'

    def reset(self):
        self.configuration = copy.deepcopy(self.b_configuration)

    def find_version(self, timeout: int = 3):
        """
        :param timeout: how much time to wait for vd version to be extracted from log (seconds)
        :return: version string if found, unknown otherwise
        """
        self.reset()
        self.run_vayadrive(autostart=True, force_run=True)
        timeout_target = time.time() + timeout  # 3 seconds
        while True:
            if time.time() > timeout_target or self.version:
                break

        self.vayadrive_process.kill()
        if not self.version:
            print('SW version details were not found!')
            return 'Unknown'
        return self.version


class VayaException(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = 'VayaException has been raised'
