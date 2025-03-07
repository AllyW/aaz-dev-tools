import os

from utils.plane import PlaneEnum
from ._swagger_module import MgmtPlaneModule, DataPlaneModule
from utils.exceptions import ResourceNotFind, InvalidAPIUsage
from ._typespec_helper import TypeSpecHelper


class SwaggerSpecs:

    def __init__(self, folder_path):
        self._folder_path = folder_path

    @property
    def spec_folder_path(self):
        return os.path.join(self._folder_path, 'specification')

    def get_mgmt_plane_modules(self, plane):
        modules = []
        for name in os.listdir(self.spec_folder_path):
            module = self.get_mgmt_plane_module(name, plane=plane)
            if module:
                modules.append(module)
        return modules

    def get_mgmt_plane_module(self, *names, plane):
        if not names:
            return None
        name = names[0]
        if not PlaneEnum.is_valid_swagger_module(plane=plane, module_name=name):
            return None

        path = os.path.join(self.spec_folder_path, name)
        if not os.path.isdir(path):
            return None
        if os.path.isdir(os.path.join(path, 'resource-manager')) or TypeSpecHelper.find_mgmt_plane_entry_files(path):
            module = MgmtPlaneModule(plane=plane, name=name, folder_path=path)
            for name in names[1:]:
                path = os.path.join(path, name)
                if not os.path.isdir(path):
                    return None
                module = MgmtPlaneModule(plane=plane, name=name, folder_path=path, parent=module)
            return module
        return None

    def get_data_plane_modules(self, plane):
        modules = []
        for name in os.listdir(self.spec_folder_path):
            module = self.get_data_plane_module(name, plane=plane)
            if module:
                modules.append(module)
        return modules

    def get_data_plane_module(self, *names, plane):
        if not names:
            return None
        name = names[0]
        if not PlaneEnum.is_valid_swagger_module(plane=plane, module_name=name):
            return None

        path = os.path.join(self.spec_folder_path, name)
        if os.path.isdir(os.path.join(path, 'data-plane')) or TypeSpecHelper.find_data_plane_entry_files(path):
            module = DataPlaneModule(plane=plane, name=name, folder_path=path)
            for name in names[1:]:
                path = os.path.join(path, name)
                if not os.path.isdir(path):
                    return None
                module = DataPlaneModule(plane=plane, name=name, folder_path=path, parent=module)
            return module

        return None


class SingleModuleSwaggerSpecs:

    def __init__(self, folder_path, module_name):
        if not os.path.isdir(folder_path):
            raise ValueError(f"Path not exist: {folder_path}")
        self._folder_path = folder_path
        self._module_name = module_name

    def get_mgmt_plane_modules(self, plane):
        names = self._module_name.split('/')
        if not PlaneEnum.is_valid_swagger_module(plane=plane, module_name=names[0]):
            raise InvalidAPIUsage(f"{names[0]} is not a valid mgmt plane module")

        if (os.path.isdir(os.path.join(self._folder_path, 'resource-manager')) or
                TypeSpecHelper.find_mgmt_plane_entry_files(self._folder_path)):
            module = None
            for name in names:
                module = MgmtPlaneModule(plane=plane, name=name, folder_path=None, parent=module)
            module.folder_path = self._folder_path
            assert module is not None
            return [module]

        raise ResourceNotFind(
            f"Cannot find manage plane module '{self._module_name}'",
            payload=f"{self._folder_path}/resource-manager is not exist"
        )

    def get_mgmt_plane_module(self, *names, plane):
        if not names:
            return None
        name = names[0]
        if not PlaneEnum.is_valid_swagger_module(plane=plane, module_name=name):
            return None

        module_str = '/'.join([plane, *names])
        module = None
        for m in self.get_mgmt_plane_modules(plane):
            if str(m) == module_str:
                module = m
                break
        return module

    def get_data_plane_modules(self, plane):
        names = self._module_name.split('/')
        if not PlaneEnum.is_valid_swagger_module(plane=plane, module_name=names[0]):
            raise InvalidAPIUsage(f"{names[0]} is not a supported data plane module.")

        if (os.path.isdir(os.path.join(self._folder_path, 'data-plane')) or
                TypeSpecHelper.find_data_plane_entry_files(self._folder_path)):
            module = None
            for name in names:
                module = DataPlaneModule(plane=plane, name=name, folder_path=None, parent=module)
            module.folder_path = self._folder_path
            assert module is not None
            return [module]

        raise ResourceNotFind(
            f"Cannot find data plane module '{self._module_name}'",
            payload=f"{self._folder_path}/data-plane is not exist"
        )

    def get_data_plane_module(self, *names, plane):
        if not names:
            return None
        name = names[0]
        if not PlaneEnum.is_valid_swagger_module(plane=plane, module_name=name):
            return None

        module_str = '/'.join([plane, *names])
        module = None
        for m in self.get_data_plane_modules(plane):
            if str(m) == module_str:
                module = m
                break
        return module
