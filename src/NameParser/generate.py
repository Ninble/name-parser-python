# clsExtractNames
#
# Parse a name into useful components.
# This class is meant to integrate the Name Parser API into your Python project.
# This class contains all functionality of the "generate" endpoint which can be found on:
# https://parser.name/api/generate-random-name/

import urllib.parse
import requests
from array import array

class clsGenerateNames:
    __apiKey = ""
    _response = {}
    _list = []
    __remaining_hour = 250  # Default rate limit
    __remaining_day = 250  # Default rate limit

    def __init__(self, apiKey) -> None:
        if(apiKey == ""):
            raise ValueError("Missing API key or API key is invalid.")

        self.__apiKey = apiKey

    def list(self) -> array:
        return self._list

    def details(self, name) -> array:
        return self._response[name]

    def response(self) -> array:
        return self._response

    def remainingHour(self) -> int:
        return self.__remaining_hour

    def remainingDay(self) -> int:
        return self.__remaining_day

    # This endpoint can generate random names for any given gender and country.
    def generate(self, results=1, gender: str = "", country_code: str = "") -> bool:

        # Create the URL with parameters depending on the input.
        url = "https://api.parser.name/?api_key=" + self.__apiKey + "&endpoint=generate&results="+urllib.parse.quote_plus(str(results))
        if(gender.lower() == "m" or gender.lower() == "f"):
            url = url+"&gender="+urllib.parse.quote_plus(gender)

        if(country_code != "" and self._validateCountryCode(country_code) == True):
            url = url+"&country_code="+urllib.parse.quote_plus(country_code)

        return self._cUrl(url)

    def _cUrl(self, url: str) -> bool:

        # Execute API request.
        response = requests.get(url)

        # Retrieve status code, header and body from response object.
        status_code = response.status_code
        header = response.headers
        json = response.json()

        # Heading contains information about rate limits.
        self._processHeader(header)

        # Process the response if possible.
        if(status_code == 200):
            if "data" in json:
                self._processResponse(json["data"])
            else:
                raise ValueError("Response is missing data.")
        else:
            raise ValueError("API returned status code "+status_code+".")

        return True

    # Retrieve variables from API response and make it available in the class.
    def _processResponse(self,response) -> None:
            
            for object in response:
                name= object['name']['firstname']['name']+" "+object['name']['lastname']['name']
                self._list.append(name)
                self._response[name]=object

    # The headers of the API response contain rate limit information.
    def _processHeader(self,header):
        
        for key,val in header.items():
            if(key=="X-Requests-Remaining-Hour"):
                self.__remaining_hour=int(val)
            if(key=="X-Requests-Remaining-Day"):
                self.__remaining_day=int(val)

    def _validateCountryCode(self,country_code) -> bool:

        country_codes={'Afghanistan' : 'AF',
                    'Albania' : 'AL',
                    'Algeria' : 'DZ',
                    'American Samoa' : 'AS',
                    'Andorra' : 'AD',
                    'Angola' : 'AO',
                    'Anguilla' : 'AI',
                    'Antarctica' : 'AQ',
                    'Antigua and Barbuda' : 'AG',
                    'Argentina' : 'AR',
                    'Armenia' : 'AM',
                    'Aruba' : 'AW',
                    'Australia' : 'AU',
                    'Austria' : 'AT',
                    'Azerbaijan' : 'AZ',
                    'Bahamas' : 'BS',
                    'Bahrain' : 'BH',
                    'Bangladesh' : 'BD',
                    'Barbados' : 'BB',
                    'Belarus' : 'BY',
                    'Belgium' : 'BE',
                    'Belize' : 'BZ',
                    'Benin' : 'BJ',
                    'Bermuda' : 'BM',
                    'Bhutan' : 'BT',
                    'Bolivia' : 'BO',
                    'Bosnia and Herzegovina' : 'BA',
                    'Botswana' : 'BW',
                    'Bouvet Island' : 'BV',
                    'Brazil' : 'BR',
                    'British Antarctic Territory' : 'BQ',
                    'British Indian Ocean Territory' : 'IO',
                    'British Virgin Islands' : 'VG',
                    'Brunei' : 'BN',
                    'Bulgaria' : 'BG',
                    'Burkina Faso' : 'BF',
                    'Burundi' : 'BI',
                    'Cambodia' : 'KH',
                    'Cameroon' : 'CM',
                    'Canada' : 'CA',
                    'Canton and Enderbury Islands' : 'CT',
                    'Cape Verde' : 'CV',
                    'Cayman Islands' : 'KY',
                    'Central African Republic' : 'CF',
                    'Chad' : 'TD',
                    'Chile' : 'CL',
                    'China' : 'CN',
                    'Paracel Islands' : 'CN',
                    'Christmas Island' : 'CX',
                    'Cocos [Keeling] Islands' : 'CC',
                    'Colombia' : 'CO',
                    'Comoros' : 'KM',
                    'Congo - Brazzaville' : 'CG',
                    'Congo - Kinshasa' : 'CD',
                    'Congo (Kinshasa)' : 'CG',
                    'Congo (Brazzaville)' : 'CG',
                    'Cook Islands' : 'CK',
                    'Costa Rica' : 'CR',
                    'Croatia' : 'HR',
                    'Cuba' : 'CU',
                    'Cyprus' : 'CY',
                    'Czech Republic' : 'CZ',
                    'Côte d’Ivoire' : 'CI',
                    'Cote D\'Ivoire' : 'CI',
                    'Denmark' : 'DK',
                    'Djibouti' : 'DJ',
                    'Dominica' : 'DM',
                    'Dominican Republic' : 'DO',
                    'Dronning Maud Land' : 'NQ',
                    'Ecuador' : 'EC',
                    'Egypt' : 'EG',
                    'El Salvador' : 'SV',
                    'Equatorial Guinea' : 'GQ',
                    'Eritrea' : 'ER',
                    'Estonia' : 'EE',
                    'Ethiopia' : 'ET',
                    'Falkland Islands' : 'FK',
                    'Faroe Islands' : 'FO',
                    'Fiji' : 'FJ',
                    'Finland' : 'FI',
                    'France' : 'FR',
                    'French Guiana' : 'GF',
                    'French Polynesia' : 'PF',
                    'French Southern Territories' : 'TF',
                    'French Southern and Antarctic Territories' : 'FQ',
                    'Gabon' : 'GA',
                    'Gambia' : 'GM',
                    'Georgia' : 'GE',
                    'Germany' : 'DE',
                    'Ghana' : 'GH',
                    'Gibraltar' : 'GI',
                    'Greece' : 'GR',
                    'Greenland' : 'GL',
                    'Grenada' : 'GD',
                    'Guadeloupe' : 'GP',
                    'Guam' : 'GU',
                    'Guatemala' : 'GT',
                    'Guernsey' : 'GG',
                    'Guinea' : 'GN',
                    'Guinea-Bissau' : 'GW',
                    'Guyana' : 'GY',
                    'Haiti' : 'HT',
                    'Heard Island and McDonald Islands' : 'HM',
                    'Honduras' : 'HN',
                    'Hong Kong SAR China' : 'HK',
                    'Hong Kong' : 'HK',
                    'Hungary' : 'HU',
                    'Iceland' : 'IS',
                    'India' : 'IN',
                    'Indonesia' : 'ID',
                    'Iran' : 'IR',
                    'Iraq' : 'IQ',
                    'Ireland' : 'IE',
                    'Isle of Man' : 'IM',
                    'Israel' : 'IL',
                    'Italy' : 'IT',
                    'Jamaica' : 'JM',
                    'Japan' : 'JP',
                    'Jersey' : 'JE',
                    'Johnston Island' : 'JT',
                    'Jordan' : 'JO',
                    'Kazakhstan' : 'KZ',
                    'Kenya' : 'KE',
                    'Kiribati' : 'KI',
                    'Kuwait' : 'KW',
                    'Kyrgyzstan' : 'KG',
                    'Laos' : 'LA',
                    'Latvia' : 'LV',
                    'Lebanon' : 'LB',
                    'Lesotho' : 'LS',
                    'Liberia' : 'LR',
                    'Libya' : 'LY',
                    'Liechtenstein' : 'LI',
                    'Lithuania' : 'LT',
                    'Luxembourg' : 'LU',
                    'Macau SAR China' : 'MO',
                    'Macedonia' : 'MK',
                    'Madagascar' : 'MG',
                    'Malawi' : 'MW',
                    'Malaysia' : 'MY',
                    'Maldives' : 'MV',
                    'Mali' : 'ML',
                    'Malta' : 'MT',
                    'Marshall Islands' : 'MH',
                    'Martinique' : 'MQ',
                    'Mauritania' : 'MR',
                    'Mauritius' : 'MU',
                    'Mayotte' : 'YT',
                    'Metropolitan France' : 'FX',
                    'Mexico' : 'MX',
                    'Micronesia' : 'FM',
                    'Federated States of Micronesia' : 'FM',
                    'Midway Islands' : 'MI',
                    'Moldova' : 'MD',
                    'Monaco' : 'MC',
                    'Mongolia' : 'MN',
                    'Montenegro' : 'ME',
                    'Montserrat' : 'MS',
                    'Morocco' : 'MA',
                    'Mozambique' : 'MZ',
                    'Myanmar [Burma]' : 'MM',
                    'Myanmar' : 'MM',
                    'Namibia' : 'NA',
                    'Nauru' : 'NR',
                    'Nepal' : 'NP',
                    'Netherlands' : 'NL',
                    'Netherlands Antilles' : 'AN',
                    'Neutral Zone' : 'NT',
                    'New Caledonia' : 'NC',
                    'New Zealand' : 'NZ',
                    'Nicaragua' : 'NI',
                    'Niger' : 'NE',
                    'Nigeria' : 'NG',
                    'Niue' : 'NU',
                    'Norfolk Island' : 'NF',
                    'North Korea' : 'KP',
                    'North Vietnam' : 'VD',
                    'Northern Mariana Islands' : 'MP',
                    'Norway' : 'NO',
                    'Oman' : 'OM',
                    'Pacific Islands Trust Territory' : 'PC',
                    'Pakistan' : 'PK',
                    'Palau' : 'PW',
                    'Palestinian Territories' : 'PS',
                    'Panama' : 'PA',
                    'Panama Canal Zone' : 'PZ',
                    'Papua New Guinea' : 'PG',
                    'Paraguay' : 'PY',
                    'People\'s Democratic Republic of Yemen' : 'YD',
                    'Peru' : 'PE',
                    'Philippines' : 'PH',
                    'Pitcairn Islands' : 'PN',
                    'Poland' : 'PL',
                    'Portugal' : 'PT',
                    'Puerto Rico' : 'PR',
                    'Qatar' : 'QA',
                    'Romania' : 'RO',
                    'Russia' : 'RU',
                    'Rwanda' : 'RW',
                    'Réunion' : 'RE',
                    'Reunion' : 'RE',
                    'Saint-Denis' : 'RE',
                    'Saint Barthélemy' : 'BL',
                    'Saint Helena' : 'SH',
                    'Saint Kitts and Nevis' : 'KN',
                    'Saint Lucia' : 'LC',
                    'Saint Martin' : 'MF',
                    'Saint Pierre and Miquelon' : 'PM',
                    'Saint Vincent and the Grenadines' : 'VC',
                    'Samoa' : 'WS',
                    'San Marino' : 'SM',
                    'Saudi Arabia' : 'SA',
                    'Senegal' : 'SN',
                    'Serbia' : 'RS',
                    'Serbia and Montenegro' : 'CS',
                    'Seychelles' : 'SC',
                    'Sierra Leone' : 'SL',
                    'Singapore' : 'SG',
                    'Slovakia' : 'SK',
                    'Slovenia' : 'SI',
                    'Solomon Islands' : 'SB',
                    'Somalia' : 'SO',
                    'South Africa' : 'ZA',
                    'South Georgia and the South Sandwich Islands' : 'GS',
                    'South Korea' : 'KR',
                    'Spain' : 'ES',
                    'Sri Lanka' : 'LK',
                    'Sudan' : 'SD',
                    'South Sudan' : 'SD',
                    'Suriname' : 'SR',
                    'Svalbard and Jan Mayen' : 'SJ',
                    'Swaziland' : 'SZ',
                    'Sweden' : 'SE',
                    'Malmö' : 'SE',
                    'Switzerland' : 'CH',
                    'Syria' : 'SY',
                    'São Tomé and Príncipe' : 'ST',
                    'Sao Tome and Principe' : 'ST',
                    'Taiwan' : 'TW',
                    'Tajikistan' : 'TJ',
                    'Tanzania' : 'TZ',
                    'Thailand' : 'TH',
                    'Timor-Leste' : 'TL',
                    'East Timor' : 'TL',
                    'Togo' : 'TG',
                    'Tokelau' : 'TK',
                    'Tonga' : 'TO',
                    'Trinidad and Tobago' : 'TT',
                    'Tunisia' : 'TN',
                    'Turkey' : 'TR',
                    'Turkmenistan' : 'TM',
                    'Turks and Caicos Islands' : 'TC',
                    'Tuvalu' : 'TV',
                    'U.S. Minor Outlying Islands' : 'UM',
                    'U.S. Miscellaneous Pacific Islands' : 'PU',
                    'U.S. Virgin Islands' : 'VI',
                    'Uganda' : 'UG',
                    'Ukraine' : 'UA',
                    'United Arab Emirates' : 'AE',
                    'United Kingdom' : 'GB',
                    'United States' : 'US',
                    'Uruguay' : 'UY',
                    'Uzbekistan' : 'UZ',
                    'Vanuatu' : 'VU',
                    'Vatican City' : 'VA',
                    'Venezuela' : 'VE',
                    'Vietnam' : 'VN',
                    'Wake Island' : 'WK',
                    'Wallis and Futuna' : 'WF',
                    'Western Sahara' : 'EH',
                    'Yemen' : 'YE',
                    'Zambia' : 'ZM',
                    'Zimbabwe' : 'ZW',
                    'Åland Islands' : 'AX',}

        if(country_code in country_codes.values()):
            return True