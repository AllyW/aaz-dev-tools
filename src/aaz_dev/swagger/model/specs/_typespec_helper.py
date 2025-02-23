import os
import logging
import re

logger = logging.getLogger('backend')


class TypeSpecHelper:

    @staticmethod
    def _iter_entry_files(folder):
        if not os.path.isdir(folder):
            raise ValueError(f"Path not exist: {folder}")
        ts_path = os.path.join(folder, "main.tsp")
        cfg_path = os.path.join(folder, "tspconfig.yaml")
        if os.path.isfile(ts_path) and os.path.isfile(cfg_path):
            yield ts_path, cfg_path
        for root, dirs, files in os.walk(folder):
            ts_path = os.path.join(root, "main.tsp")
            cfg_path = os.path.join(root, "tspconfig.yaml")
            if os.path.isfile(ts_path) and os.path.isfile(cfg_path):
                yield ts_path, cfg_path

    @classmethod
    def find_mgmt_plane_entry_files(cls, folder):
        files = []
        for ts_path, cfg_path in cls._iter_entry_files(folder):
            namespace, is_mgmt_plane = cls._parse_main_tsp(ts_path)
            if is_mgmt_plane:
                files.append((namespace, ts_path, cfg_path))
        return files

    @classmethod
    def find_data_plane_entry_files(cls, folder):
        files = []
        for ts_path, cfg_path in cls._iter_entry_files(folder):
            namespace, is_mgmt_plane = cls._parse_main_tsp(ts_path)
            if not namespace:
                continue
            if not is_mgmt_plane:
                files.append((namespace, ts_path, cfg_path))
        return files

    @classmethod
    def _parse_main_tsp(cls, path):
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        is_mgmt_plane = False
        namespace = None
        imported_tsps = []
        for line in lines:
            if line.startswith("@armProviderNamespace"):
                is_mgmt_plane = True
            if line.startswith("namespace "):
                assert namespace is None
                namespace = re.match(r"^namespace\s+([A-Za-z0-9.]+)", line).group(1)
                # armProviderNamespace will always be appeared before namespace
                break
            import_tsp = re.search(r'import\s+["\']([^"\']+\.tsp)["\']', line)
            if import_tsp:
                imported_tsps.append(import_tsp.group(1))

        if namespace is None:
            logger.info("Failed to parse main tsp file: %s namespace is not exist.", path)
            if not imported_tsps:
                return None, None
            logger.info("Try to parse namespace from the imports files %s from main tsp file: %s.", imported_tsps, path)
            return cls._parse_main_tsp_imports(path, imported_tsps)
        return namespace, is_mgmt_plane

    @classmethod
    def _parse_main_tsp_imports(cls, main_path, imported_tsps):
        base_dir = os.path.dirname(main_path)
        for check_file in imported_tsps:
            check_file_path = os.path.abspath(os.path.join(base_dir, check_file))
            is_mgmt_plane = False
            namespace = None
            with open(check_file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            for line in lines:
                if line.startswith("@armProviderNamespace"):
                    is_mgmt_plane = True
                if line.startswith("namespace "):
                    namespace = re.match(r"^namespace\s+([A-Za-z0-9.]+)", line).group(1)
                    # armProviderNamespace will always be appeared before namespace
                    break
            if namespace is not None:
                logger.info("Find namespace %s from the imports file %s.", namespace, check_file)
                return namespace, is_mgmt_plane
        return None, None

