# clsParseName
#
# Parse a name into useful components.
# This class is meant to integrate the Name Parser API into your Python project.
# This class contains all functionality of the "parse" endpoint which can be found on:
# https://parser.name/api/parse-name/
#
# Version 2.0 (23 November 2026): letter salutation in five languages, titles, suffix, middle names, name area, the
# phone hint and IPv6 addresses. password() is kept for older code but always returns "" (the API no longer returns a
# password).

import ipaddress
import requests


class clsParseName:

    def __init__(self, apiKey) -> None:
        if apiKey == "":
            raise ValueError("Missing API key or API key is invalid.")

        self._apiKey = apiKey
        self._language = ""
        self._phone = ""
        self._use_strict_validation = False
        self._remaining_hour = 250  # Default rate limit
        self._remaining_day = 250  # Default rate limit
        self._remaining_month = 0
        self._reset()

    # Every value of a parse result, reset before each request so a second request never keeps a value of the first.
    def _reset(self) -> None:
        self._response = {}
        self._salutation = ""
        self._letter = ""
        self._letter_language = ""
        self._titles = []
        self._firstname = ""
        self._middlenames = []
        self._nickname = ""
        self._lastname = ""
        self._suffix = ""
        self._gender = ""
        self._gender_formatted = ""
        self._country_code = ""
        self._country = ""
        self._country_certainty = 0
        self._name_area = ""
        self._name_area_certainty = 0
        self._currency = ""
        self._email = ""
        self._valid = False

    # The language of the letter salutation: en, nl, de, fr or es; "" lets the country of the name decide.
    def setLanguage(self, language: str) -> None:
        language = language.strip().lower()
        if language != "" and language not in ("en", "nl", "de", "fr", "es"):
            raise ValueError("The language must be one of en, nl, de, fr or es.")
        self._language = language

    # A phone number in international form (+61 2 9374 4000) as a hint for the country of the name.
    def setPhone(self, phone: str) -> None:
        self._phone = phone.strip()

    def response(self) -> dict:
        return self._response

    def salutation(self) -> str:
        return self._salutation

    # The opening line of a formal letter, such as "Dear Mr. Smith" or "Geachte heer Jansen".
    def letter(self) -> str:
        return self._letter

    def letterLanguage(self) -> str:
        return self._letter_language

    # Every title in the name, such as ["Prof.", "Dr."].
    def titles(self) -> list:
        return self._titles

    def firstname(self) -> str:
        return self._firstname

    def middlenames(self) -> list:
        return self._middlenames

    def nickname(self) -> str:
        return self._nickname

    def lastname(self) -> str:
        return self._lastname

    # Jr., Sr. or a Roman numeral such as III.
    def suffix(self) -> str:
        return self._suffix

    def gender(self) -> str:
        return self._gender

    def genderFormatted(self) -> str:
        return self._gender_formatted

    def countryCode(self) -> str:
        return self._country_code

    def country(self) -> str:
        return self._country

    def countryCertainty(self) -> int:
        return self._country_certainty

    # The group of countries that share their names through a language, such as "English" or "Spanish".
    def nameArea(self) -> str:
        return self._name_area

    def nameAreaCertainty(self) -> int:
        return self._name_area_certainty

    def currency(self) -> str:
        return self._currency

    def email(self) -> str:
        return self._email

    # Kept for older code: the API no longer returns a password.
    def password(self) -> str:
        return ""

    def valid(self) -> bool:
        return self._valid

    def remainingHour(self) -> int:
        return self._remaining_hour

    def remainingDay(self) -> int:
        return self._remaining_day

    def remainingMonth(self) -> int:
        return self._remaining_month

    # This endpoint parses a complete name and returns the first name, middle names and last name.
    # Refine is a country code (US) or an IP address (IPv4 or IPv6) of the person.
    def fromCompleteName(self, name: str, refine: str = "") -> bool:
        return self._request(self._parameters({"name": str(name)}, refine))

    # This endpoint parses an email address and returns the first name, middle names and last name.
    def fromEmailAddress(self, email: str, refine: str = "") -> bool:
        return self._request(self._parameters({"email": str(email)}, refine))

    # This endpoint parses a name and validates the name as well.
    def validate(self, name: str, refine: str = "", use_strict_validation: bool = False) -> bool:

        # Strict validation = false : The first name must exist, the lastname could be possible and the complete name should not be listed in our database with famous, fictional and humorous names.
        # Strict validation = true  : The first name and last name must exist (validated = true) and the complete name should not be listed in our database with famous, fictional and humorous names.
        self._use_strict_validation = use_strict_validation

        return self._request(self._parameters({"validate": "true", "name": str(name)}, refine), True)

    # The request parameters with the refine value, the language and the phone number.
    def _parameters(self, parameters: dict, refine: str) -> dict:
        result = {"api_key": self._apiKey, "endpoint": "parse"}
        result.update(parameters)
        if refine != "":
            if self._validateCountryCode(refine):
                result["country_code"] = refine
            else:
                try:
                    ipaddress.ip_address(refine)
                except ValueError:
                    raise ValueError("Invalid refine parameter. Refine parameter should be a country code or an IP address.")
                result["ip"] = refine
        if self._language != "":
            result["language"] = self._language
        if self._phone != "":
            result["phone"] = self._phone
        return result

    # All public functions build the parameters and use this function to execute the request. With validating, a
    # name the API cannot find or does not accept (status 404 or 400) is not valid instead of an exception.
    def _request(self, parameters: dict, validating: bool = False) -> bool:

        # Execute API request.
        response = requests.get("https://api.parser.name/", params=parameters, timeout=30)

        # Retrieve status code, header and body from response object.
        status_code = response.status_code
        try:
            json = response.json()
        except ValueError:
            json = {}

        # Heading contains information about rate limits.
        self._processHeader(response.headers)

        # Process the response if possible.
        if status_code == 200:
            if json.get("data"):
                self._processResponse(json["data"][0])
            else:
                raise ValueError("Response is missing data.")
        elif validating and status_code in (400, 404):
            self._reset()
            self._valid = False
        else:
            message = "API returned status code " + str(status_code) + "."
            if json.get("error"):
                message = message + " " + str(json["error"])
            raise ValueError(message)

        return True

    # The headers of the API response contain rate limit information.
    def _processHeader(self, header) -> None:
        if header.get("X-Requests-Remaining-Hour") is not None:
            self._remaining_hour = int(header.get("X-Requests-Remaining-Hour"))
        if header.get("X-Requests-Remaining-Day") is not None:
            self._remaining_day = int(header.get("X-Requests-Remaining-Day"))
        if header.get("X-Requests-Remaining-Month") is not None:
            self._remaining_month = int(header.get("X-Requests-Remaining-Month"))

    # Retrieve variables from API response and make it available in the class.
    def _processResponse(self, response: dict) -> None:
        self._reset()
        salutation = response.get("salutation") or {}
        name = response.get("name") or {}
        firstname = name.get("firstname") or {}
        lastname = name.get("lastname") or {}
        country = response.get("country") or {}
        email = response.get("email") or {}

        self._salutation = salutation.get("salutation") or ""
        self._letter = salutation.get("letter") or ""
        self._letter_language = salutation.get("letter_language") or ""
        self._titles = [title.get("abbriviation") for title in (response.get("titles") or []) if title.get("abbriviation")]
        self._firstname = firstname.get("name") or ""
        self._middlenames = [middle.get("name") for middle in (name.get("middlenames") or []) if middle.get("name")]
        self._nickname = name.get("nickname") or ""
        self._lastname = lastname.get("name") or ""
        self._suffix = name.get("suffix") or ""
        self._gender = firstname.get("gender") or ""
        self._gender_formatted = firstname.get("gender_formatted") or ""
        self._country_code = country.get("country_code") or ""
        self._country = country.get("name") or ""
        self._country_certainty = int(country.get("country_certainty") or 0)
        self._name_area = country.get("name_area") or ""
        self._name_area_certainty = int(country.get("name_area_certainty") or 0)
        self._currency = country.get("currency") or ""
        if isinstance(email, dict):
            self._email = email.get("address") or ""

        # If response contains validation section then it was used.
        if "validation" in response:
            if self._use_strict_validation:
                self._valid = bool(response["validation"]["pass_strict"])
            else:
                self._valid = bool(response["validation"]["pass_loose"])
        else:
            self._valid = True

        self._response = response

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
        return False
