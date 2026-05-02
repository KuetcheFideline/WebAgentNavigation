TRACKING_PATTERNS_COMPLETE = {
    
    'DIRECT_PII': [
        {
            'email_exact': r'chris\.martin\.gdpr\+FR_0417@gmail\.com',
            'email_encoded': r'chris(?:%2E|\.)martin(?:%2E|\.)gdpr(?:%2B|\+)FR_0417(?:%40|@)gmail(?:%2E|\.)com',
            'email_username': r'chris(?:%2E|\.)martin(?:%2E|\.)gdpr',
            'email_pattern': r'chris(?:%2E|\.)martin|FR_0417',
            'phone_full': r'\+33\s?656898637',
            'phone_national': r'0656898637',
            'phone_short': r'656898637',
            'phone_encoded': r'(?:%2B|\\u002B)?33\s?656898637',
            'phone_partial': r'6568986[0-9]{2}|65689863[0-9]',
            'phone_spaced': r'(?:\+33|0)\s?6\s?56\s?89\s?86\s?37',
            'full_name': r'Chris\s+Martin',
            'first_name': r'\bChris\b',
            'last_name': r'\bMartin\b',
            'name_encoded': r'Chris(?:%20|\s)Martin',
            'address_full': r'688,?\s*avenue\s+Thérèse\s+Robin',
            'address_street': r'avenue\s+Thérèse\s+Robin',
            'address_encoded': r'688(?:%2C|,)?\s*avenue(?:%20|\s)Thérèse(?:%20|\s)Robin',
            'city': r'\bRoubaix\b',
            'city_encoded': r'Roubaix',
            'birth_date_slash': r'26/11/2005',
            'birth_date_iso': r'2005-11-26',
            'birth_date_dot': r'26\.11\.2005',
            'birth_date_full': r'26[/\-\.]11[/\-\.]2005',
            'password': r'S3cur3!P@ssw0rd_2025#Complex',
            'password_encoded': r'S3cur3(?:%21|!)P(?:%40|@)ssw0rd_2025(?:%23|#)Complex',
            'gender': r'\bFemme\b|\bFemale\b',
            'postal_code_area': r'\b59\d{3}\b',
            'region': r'\bHauts-de-France\b',
            'name_and_city': r'Chris\s+Martin.*Roubaix|Roubaix.*Chris\s+Martin',
            'email_and_phone': r'chris\.martin.*656898637|656898637.*chris\.martin',
            'ip_address': r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b|\b(?:[A-F0-9]{1,4}:){7}[A-F0-9]{1,4}\b'
        },
        # ===== USER FR_0446 =====
        {
            'email_exact': r'chris\.martin\.gdpr\+FR_0446@gmail\.com',
            'email_encoded': r'chris(?:%2E|\.)martin(?:%2E|\.)gdpr(?:%2B|\+)FR_0446(?:%40|@)gmail(?:%2E|\.)com',
            'email_username': r'chris(?:%2E|\.)martin(?:%2E|\.)gdpr',
            'email_pattern': r'chris(?:%2E|\.)martin|FR_0446',
            'phone_full': r'\+33\s?606124448',
            'phone_national': r'0606124448',
            'phone_short': r'606124448',
            'phone_encoded': r'(?:%2B|\\u002B)?33\s?606124448',
            'phone_partial': r'6061244[0-9]{2}|60612444[0-9]',
            'phone_spaced': r'(?:\+33|0)\s?6\s?06\s?12\s?44\s?48',
            'full_name': r'Chris\s+Martin',
            'first_name': r'\bChris\b',
            'last_name': r'\bMartin\b',
            'name_encoded': r'Chris(?:%20|\s)Martin',
            'address_full': r'75,?\s*chemin\s+Margaux\s+Lombard',
            'address_street': r'chemin\s+Margaux\s+Lombard',
            'address_encoded': r'75(?:%2C|,)?\s*chemin(?:%20|\s)Margaux(?:%20|\s)Lombard',
            'city': r'\bParis\s+16(?:ème|e)\b',
            'city_encoded': r'Paris(?:%20|\s)16(?:ème|e)?',
            'arrondissement': r'\b75016\b',
            'birth_date_slash': r'14/05/1975',
            'birth_date_iso': r'1975-05-14',
            'birth_date_dot': r'14\.05\.1975',
            'birth_date_full': r'14[/\-\.]05[/\-\.]1975',
            'password': r'S3cur3!P@ssw0rd_2025#Complex',
            'password_encoded': r'S3cur3(?:%21|!)P(?:%40|@)ssw0rd_2025(?:%23|#)Complex',
            'gender': r'\bHomme\b|\bMale\b',
            'postal_code_area': r'\b750\d{2}\b',
            'region': r'\bIle-de-France\b',
            'marital_status': r'\bMarié\b',
            'children': r'2\s+enfants?',
            'name_and_city': r'Chris\s+Martin.*Paris|Paris.*Chris\s+Martin',
            'email_and_phone': r'chris\.martin.*606124448|606124448.*chris\.martin',
            'profession_and_city': r'Avocat.*Paris\s+16|Paris\s+16.*Avocat',
            'ip_address': r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b|\b(?:[A-F0-9]{1,4}:){7}[A-F0-9]{1,4}\b'
        },
        # ===== USER FR_0458 =====
        {
            'email_exact': r'chris\.martin\.gdpr\+FR_0458@gmail\.com',
            'email_encoded': r'chris(?:%2E|\.)martin(?:%2E|\.)gdpr(?:%2B|\+)FR_0458(?:%40|@)gmail(?:%2E|\.)com',
            'email_username': r'chris(?:%2E|\.)martin(?:%2E|\.)gdpr',
            'email_pattern': r'chris(?:%2E|\.)martin|FR_0458',
            'phone_full': r'\+33\s?653277579',
            'phone_national': r'0653277579',
            'phone_short': r'653277579',
            'phone_encoded': r'(?:%2B|\\u002B)?33\s?653277579',
            'phone_partial': r'6532775[0-9]{2}|65327757[0-9]',
            'phone_spaced': r'(?:\+33|0)\s?6\s?53\s?27\s?75\s?79',
            'full_name': r'Chris\s+Martin',
            'first_name': r'\bChris\b',
            'last_name': r'\bMartin\b',
            'name_encoded': r'Chris(?:%20|\s)Martin',
            'address_full': r'74,?\s*boulevard\s+Lenoir',
            'address_street': r'boulevard\s+Lenoir',
            'address_encoded': r'74(?:%2C|,)?\s*boulevard(?:%20|\s)Lenoir',
            'city': r'\bThibault\b',
            'city_encoded': r'Thibault',
            'birth_date_slash': r'24/01/1966',
            'birth_date_iso': r'1966-01-24',
            'birth_date_dot': r'24\.01\.1966',
            'birth_date_full': r'24[/\-\.]01[/\-\.]1966',
            'password': r'S3cur3!P@ssw0rd_2025#Complex',
            'password_encoded': r'S3cur3(?:%21|!)P(?:%40|@)ssw0rd_2025(?:%23|#)Complex',
            'gender': r'\bFemme\b|\bFemale\b',
            'employment': r'\bTemps\s+partiel\b',
            'health_marker': r'\bcancer\b',
            'household': r'parent\s+à\s+charge',
            'constraints': r'\bBurnout\b',
            'name_and_city': r'Chris\s+Martin.*Thibault|Thibault.*Chris\s+Martin',
            'email_and_phone': r'chris\.martin.*653277579|653277579.*chris\.martin',
            'aidant_context': r'aidant.*père|père.*cancer',
            'ip_address': r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b|\b(?:[A-F0-9]{1,4}:){7}[A-F0-9]{1,4}\b'
        }
    ],

    # SENSITIVE_LOCATION_PII: Technical coordinates and GPS data
    'SENSITIVE_LOCATION_PII': {
        'precise_coords': r'\b(latitude|lat|longitude|lon|lng|coords|coordinates|gps|gps_position|gps_coords|geo_position|geoposition|location_accuracy|accuracy_meters|altitude|elevation)\b',
    },

    # LOCATION_AND_DEMOGRAPHICS: General geographical and contextual data
    'LOCATION_AND_DEMOGRAPHICS': {
        'general_loc': r'\b(country|country_code|region|region_code|state|province|county|district|city|town|village|municipality|postal_code|zip|zip_code|postcode|timezone|time_zone|area_code|dialing_code|continent|continent_code|locale|language_region|string_[a-z_]+)\b',
    },

    # CONSENT_AND_PRIVACY: Privacy bars, banners, and cookies (TCF, GDPR)
    'CONSENT_AND_PRIVACY': {
        'tcf_v2': r'(tc_string|euconsent-v2|gdpr_consent|cmp_id|cmp_version)',
        'ccpa_gpp': r'(us_privacy|gpp_string|gpp_sid|usprivacy)',
        'google_consent': r'(^gcs$|^gcd$|consented_purposes|google.*consent|FCNEC|FCCDCF)',
        'trust_commander': r'(TC_PRIVACY|TC_PRIVACY_CENTER|TCPID)',
        'didomi': r'(didomi_token|didomi_cookies|didomi_dcs|didomi_but)',
        'cmp_generic': r'(consent_FID|v_acceptCookies|cookie_policy|has_consented|CMPRO|trustarc|cookieyes|usercentrics|consensu|quantcast|cmp_v2|privacy_manager)',
        'consent_management': r'(consent|CONSENTMGR|rmlconsent_)',
        'optanon': r'(Optanon|OneTrust|OptanonConsent|OptanonAlertBoxClosed)',
        'cookie_notice': r'(cookie.*notice|cookie.*alert|cookie.*banner|CookieAlert|DC-Cookie|viewed_cookie_policy|cookie_notice_accepted)',
        'gdpr_patterns': r'(\bgdpr\b|gdpr_cookie|gdpr_opt|gdpr_pd|rgpd_cookies|is_gdpr)',
        'complianz': r'(cmplz_functional|cmplz_statistics|cmplz_marketing|cmplz_banner|cmplz_policy_id)',
        'axeptio': r'(axeptio_authorized_vendors|axeptio_cookies|axeptio_all_vendors)',
        'tarteaucitron': r'(tarteaucitron)',
        'dnt_is_eu': r'(ayads-dnt|DNT|is_eu|privy|_privy_)',
    },

    # SECURITY_AND_AUTHENTICATION: All security tokens, session frameworks, and bot mitigation
    'SECURITY_AND_AUTHENTICATION': {
        'cloudflare': r'(__cf_bm|_cfuvid|cf_clearance|cf_ob_info|cf_use_ob|__cfduid|__cfruid)',
        'bot_mitigation': r'(_GRECAPTCHA|_grecaptcha|incap_ses|visid_incap|nlbi_|datadome|_abck|bm_sz|bm_sv|ak_bmsc)',
        'anti_csrf': r'(__RequestVerificationToken|csrf_token|xsrf-token|_csrf|XSRF-TOKEN|csrftoken|CRAFT_CSRF_TOKEN|LS_CSRF_TOKEN|__csrf_token-)',
        'session_frameworks': r'(_[a-z0-9_]+_session|\.AspNetCore\.[A-Za-z\.]+|\.ASPXAUTH|PHPSESSID|JSESSIONID|ASP.NET_SessionId|laravel_session|ci_session|CraftSessionId|SSESS[0-9a-f]{32}|connect.sid)',
        'auth_tokens': r'(auth_token|secure_session|login_csrf|oauth|OAuth|dtm_token|authKey|authToken|refreshToken|accessToken|nonce|keys?|tokens?|secrets?)',
        'security_monitoring': r'(sessionPrivateKey|forterToken|ddSession)',
        'cryptography': r'(hash|signature|checksum)',
    },

    # INFRASTRUCTURE_AND_TECHNICAL: Server-side markers and load balancing
    'INFRASTRUCTURE_AND_TECHNICAL': {
        'google_infrastructure': r'(__Secure-[13]PSIDCC|SIDCC|g_state|1P_JAR|NID|firebase_.*|\bfid\b)', 
        'load_balancing': r'(AWSALB|AWSALBCORS|AWSESS|SERVERID|AWSELB|AWSELIB|ARRAffinity|BIGipServer|NSC_|TS[a-f0-9]{8})',
        'cdn_routing': r'(akamai|cloudflare|fastly|cdn_|edge_)',
        'local_technical': r'(\bcluster\b|\bsp\b|\bcsd\b|\bHMS\b|\bctx\b|idb_.*|indexeddb_.*|ObjectStoreDataValue|BlobJournalEntry)',
    },

    # ADVERTISING_VENDORS: Specific trackers and sync pixels from 3rd party vendors
    'ADVERTISING_VENDORS': {
        'major_vendors': r'(id5|zeotap|mics_|pubmatic|sharedid|openx|smartadserver|contextweb|adotmob|liveramp|criteo|ttd_|TDCPM|TDID|amazon-adsystem|weborama|agkn|blismedia|creativecdn|rtbh|stackadapt|xandr|apnxs|media\.net)',
        'social_pixels': r'(_fbp|_fbc|fbclid|_ttp|_tt_|tt_pixel|li_fat_id|bcookie|linkedin|li_adsId|twitter|twclickid|_scid|_scid_r|_pin_unauth|_pinterest_)',
        'syndication_and_rtb': r'(taboola|outbrain|dmvk|dailymotion|TapAd_|bku|bkdc|bkpa|oath|guce_consent|ADGRX_CM_CASALE|pxrc|UIDR|KTPCACOOKIE)',
        'analytics_vendors': r'(Hm_|atid|atuserid|pa_user|pa_vid|_pk_|_hj|_clck|_clsk|_hjid|_hp2_|_cs_id|_chartbeat|_dd_s|ADRUM|utag_)',
        'ezoic_and_other': r'(ezo|ezux_|CoreAdsPvSession|__spdt|_cltk|algorithm_parameters.id|geoIP)',
        'yandex_metrika': r'(_ym_uid|_ym_d|_ym_isad|_ym_visorc|yandexuid|ymex|yabs-sid|metrika_enabled|_ym_metrika_enabled_)',
    },

    # NAVIGATION_AND_HISTORY: Tracking the user journey and referral sources
    'NAVIGATION_AND_HISTORY': {
        'history_and_journey': r'(visited_urls?|browsing_history|page_history|url_history|site_history|page_log|nav_stack|breadcrumb|trail|last_visited|journey_flow|click_stream|path_taken|funnel_step)',
        'referral_and_source': r'(referrer|referer|came_from|previous_page|origin_url|_orig_referrer|_landing_page|\bref\b|refer(ence|ral|rer)s?)',
        'campaign_tags': r'(utm_source|utm_medium|utm_campaign|utm_term|utm_content|campaign_id|gclid|dclid|_gac_|_gcl_|roistat_.*)',
        'interaction_logging': r'(pageCount|NbPagesVues|pageViewCounter|PageViewEvent|action|activity|events?|interact(ion)?|views?|viewer)',
    },

    # APP_STATE_AND_STORAGE: Serialized client-side data (Redux, Vue, LocalStorage)
    'APP_STATE_AND_STORAGE': {
        'state_management': r'^(persist:|redux|root_state|vuex|pinia|app_state|ngrx|store_state)',
        'generic_storage': r'(stash|blob|persist|store|cache|localStorage|sessionStorage|LFR_SESSION_STATE_|wzsession|session[0-9]+)',
        'app_config': r'(lastconfig|settings|config|localization|i18nextLng|__lsv__|oct8ne.*|feh--[a-z0-9]+|searchform)',
    },

    # CUSTOMER_AND_UX_WIDGETS: Chat support and UI interaction elements
    'CUSTOMER_AND_UX_WIDGETS': {
        'support_chats': r'(crisp-client|intercom|ZD-suid|tawkUUID|driftt_|__lc\.|uslk_umm_|LPSID-|giosg_|\bchat\b)',
        'ui_elements': r'(popup|modal|banner|overlay|toast|lightbox|omSeen-|widget|slideout|sidebar|theme|skin|layout|viewed_popup|dismissed_banner|closed_modal)',
    },

    # ECOMMERCE_AND_SALES: Shopping carts, products, and checkout states
    'ECOMMERCE_AND_SALES': {
        'cart_and_basket': r'(cart_items|basket_data|shopping_cart|cart_currency|cart_id|basket_id|WC_CartOrderId_)',
        'platform_specific': r'(mage-.*|shopify_.*|_shopify_s|_shopify_y)',
        'sales_funnel': r'(recently_viewed_product|product_id|sku|RecentProduct|checkout|order_id|sale_id|transaction_id|dwac_|lead_id|conversion_id|signup_date)',
    },

    # DIRECT_PII_KEYS: Field names that usually indicate PII storage
    'DIRECT_PII_KEYS': {
        'identity_keys': r'\b(email|mail|e-mail|e_mail|userEmail|phone|tel|telephone|mobile|cellphone|firstName|last_name|full_name|prenom|givenName|displayName|username|userName)\b',
        'address_keys': r'\b(address|street|adresse|rue|city|ville|zipCode|postal_code|postcode|cp|country|pays)\b',
        'demographic_keys': r'\b(birthDate|dob|birthday|dateNaissance|birthYear|gender|sex|sexe|genre|civilite|age|userAge|latitude|longitude|geoLocation)\b',
        'security_keys': r'\b(password|passwd|pwd|pass|motDePasse|creditCard|cardNumber|cvv|cvc|ssn|social_security|nationalId|taxId)\b',
        'account_keys': r'\b(userId|user_id|customerId|accountId|memberId|clientId|client_id)\b',
        'time_keys': r'\b(timestamp|created_at|updated_at|last_visit|event_time|session_start)\b',
    },

    # SUSPICIOUS_FORMATS: Values that look like serialized data or tokens
    'SUSPICIOUS_FORMATS': {
        'data_structures': r'(https?://|https?%3A%2F%2F|^ey[A-Za-z0-9+/]{20,}={0,2}$|^(a:\d+:\{|O:\d+:|s:\d+:)|[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$|jwtToken|__Secure-ROLLOUT_TOKEN|__ktpct)',
    },
}