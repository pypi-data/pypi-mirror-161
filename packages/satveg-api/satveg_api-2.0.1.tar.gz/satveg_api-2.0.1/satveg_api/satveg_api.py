import json
import pandas
import requests

class Series:
    """Instancia a classe Series para obtenção dos perfis temporais dos índices vegetativos NDVI ou EVI.

    Args:
        api_token (str): Token de autenticação da API SATVeg.

        profile_type (str, optional): tipo de índice a ser utilizado (ndvi ou evi). Defaults to 'ndvi'.

        satellite (str, optional): tipo de satélite a ser utilizado (terra, aqua ou comb). Defaults to 'terra'.

        pre_filter (int, optional): tipo de pré-filtro a ser utilizado. Domínio: 0 = sem pre-filtragem, 1 = correção nodata, 2 = correção nuvem, 3 = correção nuvem/nodata. Defaults to 3.

        filter (int, optional): tipo de filtro a ser utilizado. Domínio: flt = Filtro FlatBottom, wav = Filtro Wavelet, sav = Filtro Savitsky Golay. Defaults to None.

        filter_parameter (int, optional): parâmetro do filtro a ser utilizado. Este parâmetro é obrigatório para todos os filtros, exceto do tipo wav. Domínio: 0, 10, 20 ou 30 para o filtro FlatBottom; 2, 3, 4, 5 ou 6 para o filtro Savitsky Golay. Defaults to None.

    Returns:
        None
    """

    def __init__(self, api_token:str, profile_type:str='ndvi', satellite:str='terra', pre_filter:int=3, filter:int=None, filter_parameter:int=None) -> None:
        self.api_token = api_token
        self.profile_type = profile_type
        self.satellite = satellite
        self.pre_filter = pre_filter
        self.filter = filter
        self.filter_parameter = filter_parameter
        self.url = 'https://api.cnptia.embrapa.br/satveg/v1/series'

    def get_json(self, latitude:float, longitude:float) -> dict:
        """Retorna os perfis temporais dos índices vegetativos NDVI ou EVI para um ponto informado.

        Args:
            latitude (float): latitude decimal do ponto no sistema de referência EPSG 4326.

            longitude (float): longitude decimal do ponto no sistema de referência EPSG 4326.

        Returns:
            dict:
                {
                'success': True,
                'status_code': 200,
                'message': 'Sucesso.',
                'data':
                    {
                        'listaSerie': [0.607, ... , 0.7939],
                        'listaDatas': ['2000-02-18', ... , '2000-03-21']
                    }
                }
        """

        headers = {'Authorization': f'Bearer {self.api_token}'}

        parameters = {
            'tipoPerfil': self.profile_type,
            'satelite': self.satellite,
            'latitude': latitude,
            'longitude': longitude,
            'preFiltro': self.pre_filter,
            'filtro': self.filter,
            'parametroFiltro': self.filter_parameter
        }

        try:
            response = requests.get(self.url, headers=headers, params=parameters)
        except:
            return {
                'success': False,
                'status_code': 408,
                'message': 'Erro de conexão.',
                'data': {}
            }

        if response.status_code == 401:
            return {
                'success': False,
                'status_code': 401,
                'message': 'Credenciais inválidas. Verifique se você forneceu o token de autenticação correto.',
                'data': {}
            }
        elif response.status_code == 200:
            return {
                'success': True,
                'status_code': 200,
                'message': 'Sucesso.',
                'data': json.loads(response.text)
            }
        else:
            return {
                'success': False,
                'status_code': response.status_code,
                'message': 'A requisição não pode ser processada.',
                'data': {}
            }

    def get(self, latitude:float, longitude:float, label:str=None) -> pandas.DataFrame:
        """Retorna os perfis temporais dos índices vegetativos NDVI ou EVI para um ponto informado no formato Pandas.DataFrame.

        Args:
            latitude (float): latitude decimal do ponto no sistema de referência EPSG 4326.

            longitude (float): longitude decimal do ponto no sistema de referência EPSG 4326.

            label (str): label da cultura existente no terreno.

        Returns:
            pandas.DataFrame
        """

        if label is None:
            input = {
                'latitude': [latitude],
                'longitude': [longitude],
            }
        else:
            input = {
                'label': [label],
                'latitude': [latitude],
                'longitude': [longitude],
            }

        input_df = pandas.DataFrame(input)

        response = []

        for coordinates in input_df.itertuples():
            response.append(self.get_json(coordinates.latitude, coordinates.longitude))

        response_data = pandas.DataFrame(response)
        response_data = response_data.join(response_data['data'].apply(pandas.Series))
        response_data = response_data.drop('data', axis=1)

        return input_df.join(response_data)

    def from_csv(self, file:str, delimiter:str=';') -> pandas.DataFrame:
        """Retorna os perfis temporais dos índices vegetativos NDVI ou EVI para os pontos informados no arquivo csv.

        Args:
            file (str): Caminho do arquivo csv.
            delimiter (str, optional): Caractere separador de colunas do csv. Defaults to ';'.

        Returns:
            pandas.DataFrame
        """

        input_data = pandas.read_csv(file, delimiter=delimiter)
        response = []

        for coordinates in input_data.itertuples():
            response.append(self.get_json(coordinates.latitude, coordinates.longitude))

        response_data = pandas.DataFrame(response)
        response_data = response_data.join(response_data['data'].apply(pandas.Series))
        response_data = response_data.drop('data', axis=1)

        return input_data.join(response_data)

def to_learn(data:pandas.DataFrame) -> pandas.DataFrame:
    """Converte o DataFrame de entrada para o formato adequado de teste/treinamento de modelos de machine learning.

    Args:
        data (pandas.DataFrame)

    Returns:
        pandas.DataFrame
    """

    learn_data = data.loc[data['success'] == True]

    if len(learn_data.index) == 0:
        raise Exception('Nenhuma das séries possuem dados válidos.')
    else:
        response_data = pandas.DataFrame(learn_data['listaSerie'].to_list(), columns=learn_data.iloc[0]['listaDatas'])

        if 'label' in learn_data.columns:
            response_data.insert(loc=0, column='label', value=learn_data['label'].to_list())

        return response_data