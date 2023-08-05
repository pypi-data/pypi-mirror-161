import pandas as pd
from moment import moment
from ni.config import Config
from dfelf import DataFileElf
from dfelf.commons import logger


class CSVFileElf(DataFileElf):

    def __init__(self, output_dir=None, output_flag=True):
        super().__init__(output_dir, output_flag)

    def init_config(self):
        self._config = Config({
            'name': 'CSVFileElf',
            'default': {
                'add': {
                    'base': {
                        'name': 'base_filename',
                        'key': 'key_field',
                        'drop_duplicates': False,
                    },
                    'output': {
                        'name': 'output_filename',
                        'BOM': False,
                        'non-numeric': []
                    },
                    'tags': [
                        {
                            'name': 'tags_filename',
                            'key': 'key_field',
                            'fields': ['field A', 'field B'],
                            'defaults': ['default value of field A', 'default value of field B']
                        }
                    ]
                },
                'join': {
                    'base': 'base_filename',
                    'output': {
                        'name': 'output_filename',
                        'BOM': False,
                        'non-numeric': []
                    },
                    'files': [
                        {
                            'name': 'join_filename',
                            'mappings': {}
                        }
                    ]
                },
                'exclude': {
                    'input': 'input_filename',
                    'exclusion': [
                        {
                            'key': 'field',
                            'op': '=',
                            'value': 123
                        }
                    ],
                    'output': {
                        'name': 'output_filename',
                        'BOM': False,
                        'non-numeric': []
                    }
                },
                'filter': {
                    'input': 'input_filename',
                    'filters': [
                        {
                            'key': 'field',
                            'op': '=',
                            'value': 123
                        }
                    ],
                    'output': {
                        'name': 'output_filename',
                        'BOM': False,
                        'non-numeric': []
                    }
                },
                'split': {
                    'input': 'input_filename',
                    'output': {
                        'prefix': 'output_filename_prefix',
                        'BOM': False,
                        'non-numeric': []
                    },
                    'key': 'key_field'
                },
                'merge': {
                    'input': ['input_filename_01', 'input_filename_02'],
                    'output': {
                        'name': 'output_filename',
                        'BOM': False,
                        'non-numeric': []
                    },
                    'on': ['field_name'],
                    'mappings': {}
                }
            },
            'schema': {
                'type': 'object',
                'properties': {
                    'add': {
                        'type': 'object',
                        'properties': {
                            'base': {
                                'type': 'object',
                                'properties': {
                                    'name': {'type': 'string'},
                                    'key': {'type': 'string'},
                                    'drop_duplicates': {'type': 'boolean'}
                                }
                            },
                            'output': {
                                'type': 'object',
                                'properties': {
                                    'name': {'type': 'string'},
                                    'BOM': {'type': 'boolean'},
                                    'non-numeric': {
                                        'type': 'array',
                                        'items': {'type': 'string'}
                                    }
                                }
                            },
                            'tags': {
                                'type': 'array',
                                'items': {
                                    'type': 'object',
                                    'properties': {
                                        'name': {'type': 'string'},
                                        'key': {'type': 'string'},
                                        'fields': {
                                            'type': 'array',
                                            'items': {'type': 'string'}
                                        },
                                        'defaults': {
                                            'type': 'array',
                                            'items': {'type': 'string'}
                                        }
                                    }
                                },
                                'minItems': 1
                            }
                        }
                    },
                    'join': {
                        'type': 'object',
                        'properties': {
                            'base': {'type': 'string'},
                            'output': {
                                'type': 'object',
                                'properties': {
                                    'name': {'type': 'string'},
                                    'BOM': {'type': 'boolean'},
                                    'non-numeric': {
                                        'type': 'array',
                                        'items': {'type': 'string'}
                                    }
                                }
                            },
                            'files': {
                                'type': 'array',
                                'items': {
                                    'type': 'object',
                                    'properties': {
                                        'name': {'type': 'string'},
                                        'mappings': {'type': 'object'}
                                    }
                                },
                                'minItems': 1
                            }
                        }
                    },
                    'exclude': {
                        'type': 'object',
                        'properties': {
                            'input': {'type': 'string'},
                            'exclusion': {
                                'type': 'array',
                                'items': {
                                    'type': 'object',
                                    'properties': {
                                        'key': {'type': 'string'},
                                        'op': {
                                            'type': 'string',
                                            'enum': ['=', '!=', '>', '>=', '<=', '<']
                                        },
                                        'value': {'type': ['number', 'string']}
                                    }
                                }
                            },
                            'output': {
                                'type': 'object',
                                'properties': {
                                    'name': {'type': 'string'},
                                    'BOM': {'type': 'boolean'},
                                    'non-numeric': {
                                        'type': 'array',
                                        'items': {'type': 'string'}
                                    }
                                }
                            }
                        }
                    },
                    'filter': {
                        'type': 'object',
                        'properties': {
                            'input': {'type': 'string'},
                            'filters': {
                                'type': 'array',
                                'items': {
                                    'type': 'object',
                                    'properties': {
                                        'key': {'type': 'string'},
                                        'op': {
                                            'type': 'string',
                                            'enum': ['=', '!=', '>', '>=', '<=', '<']
                                        },
                                        'value': {'type': ['number', 'string']}
                                    }
                                }
                            },
                            'output': {
                                'type': 'object',
                                'properties': {
                                    'name': {'type': 'string'},
                                    'BOM': {'type': 'boolean'},
                                    'non-numeric': {
                                        'type': 'array',
                                        'items': {'type': 'string'}
                                    }
                                }
                            }
                        }
                    },
                    'split': {
                        'type': 'object',
                        'properties': {
                            'input': {'type': 'string'},
                            'output': {
                                'type': 'object',
                                'properties': {
                                    'prefix': {'type': 'string'},
                                    'BOM': {'type': 'boolean'},
                                    'non-numeric': {
                                        'type': 'array',
                                        'items': {'type': 'string'}
                                    }
                                }
                            },
                            'key': {'type': 'string'}
                        }
                    },
                    'merge': {
                        'type': 'object',
                        'properties': {
                            'input': {
                                'type': 'array',
                                'items': {'type': 'string'},
                                'minItems': 2
                            },
                            'output': {
                                'type': 'object',
                                'properties': {
                                    'prefix': {'type': 'string'},
                                    'BOM': {'type': 'boolean'},
                                    'non-numeric': {
                                        'type': 'array',
                                        'items': {'type': 'string'}
                                    }
                                }
                            },
                            'on': {
                                'type': 'array',
                                'items': {'type': 'string'},
                                'minItems': 1
                            },
                            'mappings': {'type': 'object'}
                        }
                    }
                }
            }
        })

    def to_output(self, task_key, **kwargs):
        if task_key == 'split':
            output_prefix = ''
            if '' != self._config[task_key]['output']['prefix']:
                output_prefix = self._config[task_key]['output']['prefix'] + '_'
            non_numeric = self._config[task_key]['output']['non-numeric']
            output_filename = self.get_output_path(output_prefix + kwargs['filename'] + '.csv')
            if self._output_flag:
                pass
            else:
                output_filename = self.get_log_path(output_prefix + kwargs['filename'] + '.csv')
            bom = self._config[task_key]['output']['BOM']
            CSVFileElf.to_csv(kwargs['df'], output_filename, bom, non_numeric)
        else:
            output_filename = self.get_output_path(self._config[task_key]['output']['name'])
            if self._output_flag:
                pass
            else:
                output_filename = self.get_log_path(self._config[task_key]['output']['name'])
            bom = self._config[task_key]['output']['BOM']
            nn = self._config[task_key]['output']['non-numeric']
            CSVFileElf.to_csv(kwargs['df'], output_filename, bom, nn)

    def drop_duplicates(self, df, subset):
        if isinstance(subset, str):
            subset_value = [subset]
        elif isinstance(subset, list):
            subset_value = subset.copy()
        else:
            raise TypeError(logger.error([2003, subset, type(subset)]))
        mask = pd.Series(df.duplicated(subset=subset_value))
        log_filename = 'drop_duplicates' + moment().format('.YYYYMMDD.HHmmss') + '.log'
        filename = self.get_log_path(log_filename)
        log_filename_pre = 'pre_' + log_filename
        pre_filename = self.get_log_path(log_filename_pre)
        duplicates = df[mask]
        else_mask = ~ mask
        if not duplicates.empty:
            CSVFileElf.to_csv_with_bom(duplicates, filename)
            tmp_df = df[df[subset_value].isin(duplicates[subset_value])]
            logger.warning([2000, log_filename_pre, tmp_df.sort_values(by=subset_value)])
            CSVFileElf.to_csv_with_bom(tmp_df, pre_filename)
            logger.warning([2001, log_filename, duplicates])
        return df[else_mask], log_filename

    @staticmethod
    def tidy(df, nn):
        df_export = df.copy()
        for field in nn:
            if field in df_export.columns:
                df_export[field] = df_export[field].apply(lambda x: '="' + x + '"')
        return df_export

    @staticmethod
    def to_csv(df, output_filename, bom, non_numeric=None):
        nn = non_numeric if non_numeric else []
        if bom:
            CSVFileElf.to_csv_with_bom(df, output_filename, nn)
        else:
            CSVFileElf.to_csv_without_bom(df, output_filename, nn)

    @staticmethod
    def to_csv_without_bom(df, output_filename, non_numeric=None):
        nn = non_numeric if non_numeric else []
        df_export = CSVFileElf.tidy(df, nn)
        df_export.to_csv(output_filename, index=False)

    @staticmethod
    def to_csv_with_bom(df, output_filename, non_numeric=None):
        nn = non_numeric if non_numeric else []
        df_export = CSVFileElf.tidy(df, nn)
        df_export.to_csv(output_filename, index=False, encoding='utf-8-sig')

    @staticmethod
    def read_content(cvs_filename):
        content = pd.read_csv(cvs_filename, dtype=str)
        return content

    def add(self, input_obj: pd.DataFrame = None, silent: bool = False, **kwargs):
        task_key = 'add'
        self.set_config_by_task_key(task_key, **kwargs)
        if input_obj is None:
            if self.is_default(task_key):
                return None
            else:
                df_ori = CSVFileElf.read_content(self._config[task_key]['base']['name'])
        else:
            df_ori = input_obj.copy()
        key_ori = self._config[task_key]['base']['key']
        if self._config[task_key]['base']['drop_duplicates']:
            df_ori = self.drop_duplicates(df_ori, key_ori)[0]
        for tag in self._config[task_key]['tags']:
            df_tag = CSVFileElf.read_content(tag['name'])
            key_right = tag['key']
            df_tag = self.drop_duplicates(df_tag, key_right)[0]
            fields = tag['fields']
            defaults = tag['defaults']
            columns = df_tag.columns
            for col in columns:
                if col in fields or col == key_right:
                    pass
                else:
                    df_tag.drop([col], axis=1, inplace=True)
            df_tag.rename(columns={key_right: key_ori}, inplace=True)
            df_ori = pd.merge(df_ori, df_tag, how="left", left_on=key_ori, right_on=key_ori)
            for x in range(len(fields)):
                df_ori[fields[x]].fillna(defaults[x], inplace=True)
        if silent:
            pass
        else:
            self.to_output(task_key, df=df_ori)
        return df_ori

    def join(self, input_obj: pd.DataFrame = None, silent: bool = False, **kwargs):
        task_key = 'join'
        self.set_config_by_task_key(task_key, **kwargs)
        if input_obj is None:
            if self.is_default(task_key):
                return None
            else:
                df_ori = CSVFileElf.read_content(self._config[task_key]['base'])
        else:
            df_ori = input_obj.copy()
        files = self._config[task_key]['files']
        for file in files:
            df = CSVFileElf.read_content(file['name'])
            if len(file['mappings']) > 0:
                # for key, value in file['mappings'].items():
                #     df.rename(columns={key: value}, inplace=True)
                df.rename(columns=file['mappings'], inplace=True)
            df_ori = df_ori.append(df)
        if silent:
            pass
        else:
            self.to_output(task_key, df=df_ori)
        return df_ori

    def exclude(self, input_obj: pd.DataFrame = None, silent: bool = False, **kwargs):
        task_key = 'exclude'
        self.set_config_by_task_key(task_key, **kwargs)
        if input_obj is None:
            if self.is_default(task_key):
                return None
            else:
                df_ori = CSVFileElf.read_content(self._config[task_key]['input'])
        else:
            df_ori = input_obj.copy()
        exclusion = self._config[task_key]['exclusion']
        for e in exclusion:
            key = e['key']
            op = e['op']
            value = e['value']
            if isinstance(value, str):
                if '=' == op:
                    df_ori = df_ori.loc[df_ori[key] != value]
                    continue
                if '!=' == op:
                    df_ori = df_ori.loc[df_ori[key] == value]
                    continue
                if '>' == op:
                    df_ori = df_ori.loc[df_ori[key] <= value]
                    continue
                if '>=' == op:
                    df_ori = df_ori.loc[df_ori[key] < value]
                    continue
                if '<' == op:
                    df_ori = df_ori.loc[df_ori[key] >= value]
                    continue
                if '<=' == op:
                    df_ori = df_ori.loc[df_ori[key] > value]
                    continue
            else:
                key_tmp = key + '_tmp'
                df_ori[key_tmp] = df_ori[key].apply(lambda x: float(x))
                if '=' == op:
                    df_ori = df_ori.loc[df_ori[key_tmp] != value].drop(columns=[key_tmp])
                    continue
                if '!=' == op:
                    df_ori = df_ori.loc[df_ori[key_tmp] == value].drop(columns=[key_tmp])
                    continue
                if '>' == op:
                    df_ori = df_ori.loc[df_ori[key_tmp] <= value].drop(columns=[key_tmp])
                    continue
                if '>=' == op:
                    df_ori = df_ori.loc[df_ori[key_tmp] < value].drop(columns=[key_tmp])
                    continue
                if '<' == op:
                    df_ori = df_ori.loc[df_ori[key_tmp] >= value].drop(columns=[key_tmp])
                    continue
                if '<=' == op:
                    df_ori = df_ori.loc[df_ori[key_tmp] > value].drop(columns=[key_tmp])
                    continue
        if silent:
            pass
        else:
            self.to_output(task_key, df=df_ori)
        return df_ori

    def filter(self, input_obj: pd.DataFrame = None, silent: bool = False, **kwargs):
        task_key = 'filter'
        self.set_config_by_task_key(task_key, **kwargs)
        if input_obj is None:
            if self.is_default(task_key):
                return None
            else:
                df_ori = CSVFileElf.read_content(self._config[task_key]['input'])
        else:
            df_ori = input_obj.copy()
        filters = self._config[task_key]['filters']
        for f in filters:
            key = f['key']
            op = f['op']
            value = f['value']
            if isinstance(value, str):
                if '=' == op:
                    df_ori = df_ori.loc[df_ori[key] == value]
                    continue
                if '!=' == op:
                    df_ori = df_ori.loc[df_ori[key] != value]
                    continue
                if '>' == op:
                    df_ori = df_ori.loc[df_ori[key] > value]
                    continue
                if '>=' == op:
                    df_ori = df_ori.loc[df_ori[key] >= value]
                    continue
                if '<' == op:
                    df_ori = df_ori.loc[df_ori[key] < value]
                    continue
                if '<=' == op:
                    df_ori = df_ori.loc[df_ori[key] <= value]
                    continue
            else:
                key_tmp = key + '_tmp'
                df_ori[key_tmp] = df_ori[key].apply(lambda x: float(x))
                if '=' == op:
                    df_ori = df_ori.loc[df_ori[key_tmp] == value].drop(columns=[key_tmp])
                    continue
                if '!=' == op:
                    df_ori = df_ori.loc[df_ori[key_tmp] != value].drop(columns=[key_tmp])
                    continue
                if '>' == op:
                    df_ori = df_ori.loc[df_ori[key_tmp] > value].drop(columns=[key_tmp])
                    continue
                if '>=' == op:
                    df_ori = df_ori.loc[df_ori[key_tmp] >= value].drop(columns=[key_tmp])
                    continue
                if '<' == op:
                    df_ori = df_ori.loc[df_ori[key_tmp] < value].drop(columns=[key_tmp])
                    continue
                if '<=' == op:
                    df_ori = df_ori.loc[df_ori[key_tmp] <= value].drop(columns=[key_tmp])
                    continue
        if silent:
            pass
        else:
            self.to_output(task_key, df=df_ori)
        return df_ori

    def split(self, input_obj: pd.DataFrame = None, silent: bool = False, **kwargs):
        task_key = 'split'
        self.set_config_by_task_key(task_key, **kwargs)
        if input_obj is None:
            if self.is_default(task_key):
                return None
            else:
                input_filename = self._config[task_key]['input']
                df_ori = CSVFileElf.read_content(input_filename)
        else:
            input_filename = '<内存对象>'
            df_ori = input_obj.copy()
        key_name = self._config[task_key]['key']
        columns = df_ori.columns
        res = []
        if key_name in columns:
            split_keys = df_ori[key_name].unique()
            if silent:
                for key in split_keys:
                    tmp_df = df_ori.loc[df_ori[key_name] == key]
                    res.append(tmp_df)
            else:
                for key in split_keys:
                    tmp_df = df_ori.loc[df_ori[key_name] == key]
                    self.to_output(task_key, df=tmp_df, filename=key)
                    res.append(tmp_df)
            return res
        else:
            raise KeyError(logger.error([2002, input_filename, key_name]))

    def merge(self, input_obj: list = None, silent: bool = False, **kwargs):
        task_key = 'merge'
        self.set_config_by_task_key(task_key, **kwargs)
        if input_obj is None:
            if self.is_default(task_key):
                return None
            else:
                inputs = self._config[task_key]['input']
                df_ori = []
                for input_filename in inputs:
                    df = CSVFileElf.read_content(input_filename)
                    df_ori.append(df)
        else:
            inputs = '<内存对象>'
            df_ori = input_obj.copy()
        mappings = self._config[task_key]['mappings']
        if len(mappings) > 0:
            for df in df_ori:
                df.rename(columns=mappings, inplace=True)
        on_cols = self._config[task_key]['on']
        df_on = pd.DataFrame([], columns=on_cols)
        all_cols = []
        for df in df_ori:
            df_on = df_on.append(df[on_cols])
            all_cols = all_cols + list(set(df.columns) - set(all_cols))
        all_cols.sort()
        for col in on_cols:
            all_cols.remove(col)
        all_cols = on_cols + all_cols
        df_res = pd.DataFrame([], columns=all_cols)
        df_on, log_file = self.drop_duplicates(df_on, on_cols)
        df_on.reset_index(drop=True, inplace=True)
        df_res[on_cols] = df_on[on_cols]
        for df in df_ori:
            df_adj = self.drop_duplicates(df, on_cols)[0]
            index = df_on[df_on.set_index(on_cols).index.isin(df_adj.set_index(on_cols).index)].index
            df_adj.set_index(index, inplace=True)
            df_res[df_res.isnull()] = df_adj
        if silent:
            pass
        else:
            self.to_output(task_key, df=df_res)
        return df_res
