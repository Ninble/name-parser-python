# clsParseName
#
# Parse a name into useful components.
# This class is meant to integrate the Name Parser API into your PHP project.
# This class contains all functionality of the "parse" endpoint which can be found on:
# https://parser.name/api/parse-name/

import urllib.parse
import ipaddress
import requests
from array import array

class clsParseName:

    _apiKey = ""
    _use_strict_validation = False
    _response = []
    _salutation = ""
    _firstname = ""
    _nickname = ""
    _lastname = ""
    _gender = ""
    _gender_formatted = ""
    _country_code = ""
    _country = ""
    _currency = ""
    _email = ""
    _password = ""
    _valid = False

    _remaining_hour = 250 #Default rate limit
    _remaining_day = 250 #Default rate limit

    def __init__(self,apiKey) -> None:
        if(apiKey == ""):
            raise ValueError("Missing API key or API key is invalid.")

        self._apiKey = apiKey

    def response(self) -> array:
        return self._response

    def salutation(self) ->str:

        return self._salutation

    def firstname(self)->str:
        return self._firstname

    def nickname(self)->str:
        return self._nickname

    def lastname(self)->str:
        return self._lastname

    def gender(self)->str:
        return self._gender

    def genderFormatted(self)->str:
        return self._gender_formatted

    def countryCode(self)->str:
        return self._country_code

    def country(self)->str:
        return self._country

    def currency(self)->str:
        return self._currency

    def email(self)->str:
        return self._email

    def password(self)->str:
        self._password

    def valid(self)->bool:
        return self._valid

    def remainingHour(self)->int:
        return self._remaining_hour

    def remainingDay(self)->int:
        return self._remaining_day

    # This endpoint parses a complete name and returns the first name, middle names and last name.
    def fromCompleteName(self,name:str,refine:str="")->bool:

        # Create the URL with parameters depending on the input.
        url = "https://api.parser.name/?api_key=" + self._apiKey + "&endpoint=parse&name="+urllib.parse.quote_plus(str(name))

        if(refine != ""):
            try:
                if(self._validateCountryCode(refine)):
                    url=url+"&country_code="+refine
                elif (ipaddress.ip_address(refine).version==4):
                    url=url+"&ip="+refine
            except:
                raise ValueError("Invalid refine parameter. Refine parameter should be country code or IPv4 address.")
        
        return self._cUrl(url)

    # This endpoint parses an email address and returns the first name, middle names and last name.
    def fromEmailAddress(self,email,refine:str="")->bool:

        # Create the URL with parameters depending on the input.
        url = "https://api.parser.name/?api_key=" +self._apiKey + "&endpoint=parse&email="+urllib.parse.quote_plus(str(email))
        if(refine != ""):
            try:
                if(self._validateCountryCode(refine)):
                    url=url+"&country_code="+refine
                elif (ipaddress.ip_address(refine).version==4):
                    url=url+"&ip="+refine
            except:
                raise ValueError("Invalid refine parameter. Refine parameter should be country code or IPv4 address.")
        
        return self._cUrl(url)

    # This endpoint parses a name and validates the name as well.
    def validate(self,name:str, refine:str="",use_strict_validation:bool=False)->bool:

        # Strict validation = false : The first name must exist, the lastname could be possible and the complete name should not be listed in our database with famous, fictional and humorous names.
        # Strict validation = true  : The first name and last name must exist (validated = true) and the complete name should not be listed in our database with famous, fictional and humorous names.
        
        self._use_strict_validation=use_strict_validation

        # Create the URL with parameters depending on the input.
        url = "https://api.parser.name/?api_key=" +self._apiKey +"&endpoint=parse&validate=true&name="+urllib.parse.quote_plus(str(name))
        if(refine != ""):
            try:
                if(self._validateCountryCode(refine)):
                    url=url+"&country_code="+refine
                elif (ipaddress.ip_address(refine).version==4):
                    url=url+"&ip="+refine
            except:
                raise ValueError("Invalid refine parameter. Refine parameter should be country code or IPv4 address.")
        
        return self._cUrl(url)    
    
    # All public functions create a URL and use this curl function to execute the request.
    def _cUrl(self,url:str)->bool:

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
            if json["data"][0]:
                
                self._processResponse(json["data"][0])
            else:
                raise ValueError("Response is missing data.")
        else:
            raise ValueError("API returned status code "+status_code+".")

        return True

    def _processHeader(self,header):
        
        for key,val in header.items():
            if(key=="X-Requests-Remaining-Hour"):
                self._remaining_hour=int(val)
            if(key=="X-Requests-Remaining-Day"):
                self._remaining_day=int(val)

    def _processResponse(self,response,validate:bool=False)->bool:

        if response['salutation'] is not None:
            self._salutation=response['salutation']['salutation']
        
        if response['name']['firstname'] is not None:
            self._firstname=response['name']['firstname']['name']
        
        if response['name']['nickname'] is not None:
            self._nickname=response['name']['nickname']['name']
        
        if response['name']['lastname'] is not None:
            self._lastname=response['name']['lastname']['name']

        if response['name']['firstname'] is not None:
            self._gender=response['name']['firstname']['gender']

        if response['name']['firstname'] is not None:
            self._gender_formatted=response['name']['firstname']['gender_formatted']
        
        if response['country'] is not None:
            self._country_code=response['country']['country_code']

        if response['country'] is not None:
            self._country=response['country']['name']
        
        if response['country'] is not None:
            self._currency=response['country']['currency']

        if response['email'] is not None:
            self._email=response['email']['address']
        
        if "password" in response :
            self._password=response['password']

        # If response contains validation section then it was used.
        if 'validation' in response:
            if(self._use_strict_validation==True):
                self._valid=bool(response['validation']['pass_strict'])
            else:
                self._valid=bool(response['validation']['pass_loose'])
        else:
            self._valid=True
        
        self._response=response

    # Check if a given country code is valid.
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
                    'Åland Islands' : 'AX'}

        if(country_code in country_codes.values()):
            return True