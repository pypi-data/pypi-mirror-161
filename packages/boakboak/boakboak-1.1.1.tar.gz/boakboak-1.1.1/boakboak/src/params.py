# params.py
import os, yaml
import boakboak.src.settings as sts
import time


class Params:
    def __init__(self):
        # if the yml file is found inside the app folder appDefault == True else False
        self.appDefault = False
        self.params = {}
        self.extParams = {}

    def get_params(
        self,
        apps: list,
        *args,
        appsParamsDir: str = sts.appsParamsDir,
        **kwargs,
    ) -> dict:
        # getting runtime parameters and returning them
        # takes apps name and returns a list of dictionaries
        try:
            for app in apps:
                appsParamsDir, fileName = self.get_params_file(app, appsParamsDir)
                with open(os.path.join(appsParamsDir, fileName)) as f:
                    self.params.update({app: yaml.safe_load(f)})
                if self.appDefault:
                    self.params = self.import_external_sub_cmds(appsParamsDir, app)
                self.params[app].update({"appsParamsDir": appsParamsDir})
                self.params[app].update({"app": app})
                if self.params[app]["appPath"] in sts.appPathAliass:
                    self.params[app]["appPath"] = appsParamsDir
        except Exception as e:
            print(f"Params.get_params: {e} not found! Sure it exists?")
            print(f"{sts.appsParamsDir = }")
            exit()
        return self.params

    def import_external_sub_cmds(self, appsParamsDir: str, app: str) -> dict[dict, str]:
        """
        boakboak can take cmds from another file i.e. .gitlab-ci.yml
        this will read the external params path from the cmds key in .yml
        p[0] will be the fileName p[1] ... is the path to cmds
        see also README.md
        """
        cmds = self.params[app].get("cmds")
        if type(cmds) == str:
            p = cmds.replace(" ", "").split(",")
            with open(os.path.join(appsParamsDir, f"{p[0]}{sts.pFileExt}")) as f:
                self.extParams.update({app: yaml.safe_load(f)})
            self.params[app]["cmds"] = self.extParams[app].get(p[1]).get(p[2])[0].split()
        return self.params

    def get_params_file(self, app: str, appsParamsDir) -> str:
        """
        takes a param directory and checks if the fileName exsits as a file within
        the directory, if it exsits it returns both the directory and the fileName
        if fileName is not found, it tries to fine the fileName within the app itself
        this should look like: ./appName/appName.yml
        """
        fileName = f"{app}{sts.pFileExt}"
        filePath = os.path.join(appsParamsDir, fileName)
        if not os.path.isfile(filePath):
            return self.find_package_params_file(app)
        else:
            return appsParamsDir, fileName

    def find_package_params_file(self, app: str, *args, **kwargs) -> tuple[str]:
        """
        searches for the params file within the file structure of the target app itself
        the app could be at any location wihtin the target apps main directory
        this should look like: ./appName/appName.yml
        """
        Params.check_search_path(*args, **kwargs)
        # search happends here
        start, cnt = time.time(), 0
        for _dir, dirs, files in os.walk(sts.searchBase):
            cnt += 1
            if time.time() - start > sts.searchTimeout:
                break
            if not app in _dir:
                continue
            if len(_dir.split(os.sep)) > sts.maxD:
                continue
            if _dir.endswith(app):
                fileNames = [
                    f
                    for f in files
                    if f.startswith(sts.pgParamPrefix) and f.endswith(sts.pFileExt)
                ]
                for fileName in fileNames:
                    if os.path.isfile(os.path.join(_dir, fileName)):
                        self.appDefault = True
                        return sts.os_sep(_dir), fileName
        print(f"find_package_params_file: searched {cnt} dirs: Timeout {sts.searchTimeout}s")
        return None, app

    def get_all_apps(
        self, app: str, *args, appsParamsDir: str = sts.appsParamsDir, **kwargs
    ) -> list[str]:
        """
        when the user provides * instead of app name,
        all apps are loaded from apps directory
        """
        if app == sts.allApps:
            apps = [f[:-4] for f in os.listdir(appsParamsDir) if f.endswith(sts.pFileExt)]
            assert apps, f"apps not found: {app}"
        else:
            apps = [f"{app}"]
        return apps

    @staticmethod
    def check_search_path(*args, **kwargs):
        # search should not include os folders, therefore must be limited
        if len([b for b in sts.searchBase.split(os.sep) if b]) < sts.minD:
            print(f"\nSearch base {sts.searchBase} to large:")
            print(f"{os.listdir(sts.searchBase) = }")
            print("\n")
            sts.searchBase = os.path.join(
                sts.searchBase, input(f"Name one search dir from above: ")
            )
