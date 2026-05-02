# regex_master.py - La version la plus complète et optimisée

TRACKING_PATTERNS_COMPLETE = {
    
    # ===== SECTION 1: DONNÉES IDENTIFIANTES DIRECTES (PII) POUR TESTS =====
    # Issu de regex.py v2 - Profils spécifiques pour les tests de fuite
    'DIRECT_PII': [
        # USER FR_0417
        {
            'email_exact': r'chris\.martin\.gdpr\+FR_0417@gmail\.com',
            'email_encoded': r'chris(?:%2E|\.)martin(?:%2E|\.)gdpr(?:%2B|\+)FR_0417(?:%40|@)gmail(?:%2E|\.)com',
            'phone_full': r'\+33\s?656898637',
            'phone_national': r'0656898637',
            'full_name': r'Chris\s+Martin',
            'address_full': r'688,?\s*avenue\s+Thérèse\s+Robin',
            'city': r'\bRoubaix\b',
            'birth_date': r'26[/\-\.]11[/\-\.]2005',
            'password': r'S3cur3!P@ssw0rd_2025#Complex',
            'ip_address': r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'
        },
        # USER FR_0446
        {
            'email_exact': r'chris\.martin\.gdpr\+FR_0446@gmail\.com',
            'email_encoded': r'chris(?:%2E|\.)martin(?:%2E|\.)gdpr(?:%2B|\+)FR_0446(?:%40|@)gmail(?:%2E|\.)com',
            'phone_full': r'\+33\s?606124448',
            'phone_national': r'0606124448',
            'full_name': r'Chris\s+Martin',
            'address_full': r'75,?\s*chemin\s+Margaux\s+Lombard',
            'city': r'\bParis\s+16(?:ème|e)\b',
            'arrondissement': r'\b75016\b',
            'birth_date': r'14[/\-\.]05[/\-\.]1975',
            'ip_address': r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'
        },
        # USER FR_0458
        {
            'email_exact': r'chris\.martin\.gdpr\+FR_0458@gmail\.com',
            'email_encoded': r'chris(?:%2E|\.)martin(?:%2E|\.)gdpr(?:%2B|\+)FR_0458(?:%40|@)gmail(?:%2E|\.)com',
            'phone_full': r'\+33\s?653277579',
            'phone_national': r'0653277579',
            'full_name': r'Chris\s+Martin',
            'address_full': r'74,?\s*boulevard\s+Lenoir',
            'city': r'\bThibault\b',
            'birth_date': r'24[/\-\.]01[/\-\.]1966',
            'health_marker': r'\bcancer\b',
            'constraints': r'\bBurnout\b',
            'ip_address': r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'
        }
    ],

    # ===== SECTION 2: CONSENTEMENT ET VIE PRIVÉE (RGPD/TCF/CCPA) =====
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
        'axeptio_tarteaucitron': r'(axeptio_authorized_vendors|axeptio_cookies|axeptio_all_vendors|tarteaucitron)',
        'dnt_is_eu': r'(ayads-dnt|DNT|is_eu|privy|_privy_)',
        'sddan_cmp_val': r'(sddan:cmp|eqtv_cmpvalid|_wpinitialpermissionstate)',
    },

    # ===== SECTION 3: SÉCURITÉ, BOT ET AUTHENTIFICATION =====
    'SECURITY_AND_AUTH': {
        'cloudflare': r'(__cf_bm|_cfuvid|cf_clearance|cf_ob_info|cf_use_ob|__cfduid|__cfruid)',
        'bot_mitigation': r'(_GRECAPTCHA|_grecaptcha|incap_ses|visid_incap|nlbi_|datadome|_abck|bm_sz|bm_sv|ak_bmsc)',
        'anti_csrf': r'(__RequestVerificationToken|csrf_token|xsrf-token|_csrf|XSRF-TOKEN|csrftoken|CRAFT_CSRF_TOKEN|LS_CSRF_TOKEN|__csrf_token-)',
        'framework_sessions': r'(_[a-z0-9_]+_session|\.AspNetCore\.[A-Za-z\.]+|\.ASPXAUTH|PHPSESSID|JSESSIONID|ASP.NET_SessionId|laravel_session|ci_session|CraftSessionId|SSESS[0-9a-f]{32}|connect.sid)',
        'auth_tokens': r'(auth_token|secure_session|login_csrf|oauth|OAuth|dtm_token|authKey|authToken|refreshToken|accessToken|nonce|keys?|tokens?|secrets?)',
        'security_monitoring': r'(sessionPrivateKey|forterToken|ddSession)',
        'cryptography': r'(hash|signature|checksum|verif(y|ied)|secur(e|ity))',
    },

    # ===== SECTION 4: RÉGIES PUBLICITAIRES ET VENDUERS (ADTECH) =====
    'ADVERTISING_VENDORS': {
        'major_ids_sync': r'(\bid5\b|id5-sync|id5id|^3pi$|zeotap|mics_|pubmatic|sharedid|openx|smartadserver|contextweb|adotmob|liveramp|ttd_|TDCPM|TDID|amazon-adsystem|weborama|agkn|blismedia|creativecdn|rtbh|stackadapt|xandr|apnxs|media\.net)',
        'criteo_extended': r'(criteo|cto_bundle|cto_bidid|cto_id|cto_lwid|cto_writeable|cto_tld_test)',
        'social_pixels': r'(_fbp|_fbc|fbclid|_ttp|_tt_|tt_pixel|li_fat_id|bcookie|linkedin|li_adsId|UserMatchHistory|li_sugr|twitter|twclickid|twid|^muc$|_scid|_scid_r|_pin_unauth|_pinterest_)',
        'syndication_rtb': r'(taboola|outbrain|obuid|t_gid|trc_cookie_storage|dmvk|dailymotion|TapAd_|bku|bkdc|bkpa|oath|guce_consent|ADGRX_CM_CASALE|pxrc|UIDR|KTPCACOOKIE|CMRUM3|OT_)',
        'yandex_baidu': r'(_ym_uid|_ym_visorc|yandexuid|ymex|yabs-sid|metrika_enabled|Hm_)',
        'ezoic_generic': r'(ezo|ezux_|CoreAdsPvSession|__spdt|_cltk|algorithm_parameters.id|geoIP)',
    },

    # ===== SECTION 5: ANALYTICS ET COMPORTEMENT (UX) =====
    'ANALYTICS_AND_BEHAVIOR': {
        'google_stack': r'(^_ga$|_ga_|_gid|_gat|__utma|__utmb|__utmz|gclid|dclid|_gac_|_gcl_|gtm_|^__gads$|^__gpi$|GoogleAdServingTest|_dc_gtm_)',
        'adobe_piano': r'(s_cc|s_plt|s_ppv|s_ips|s_vi|s_fid|mbox|demdex|AMCV_|AMCVS_|kndctr_|_pctx|_pcid|piano|pa_user|pa_vid)',
        'hotjar_clarity_session': r'(_hjSession|_hjUserId|_clck|_clsk|_hjid|_hjFirstSeen|_hp2_|fs_uid|fs_interim|_ceg|_ces|logrocket|^lr_|mf_user|mf_session|CLID)',
        'ux_metrics': r'(_cs_id|_cs_mk|_cs_root|_chartbeat|_cb_svref|_cb_ls|_dd_s|_dd_r|ADRUM|utag_|atid|atuserid|_pk_)',
        'behavioral_tracking': r'(mouse_pos|cursor_x|mouse_move|scroll_depth|scroll_pos|max_scroll|keystroke|input_tracking|form_analytics|field_focus|typing_speed|tap_targets)',
        'ab_testing': r'(ab\.storage|ab_test|ab_group|_abck|AB_|obs_ab|ezoab_|experiment_|ABTest_|abtasty|kameleoon|acid_booking|acid_search)',
    },

    # ===== SECTION 6: NAVIGATION ET HISTORIQUE =====
    'NAVIGATION_HISTORY': {
        'history_and_journey': r'(visited_urls?|browsing_history|page_history|url_history|site_history|page_log|nav_stack|breadcrumb|trail|last_visited|journey_flow|click_stream|path_taken|funnel_step)',
        'referral_and_source': r'(referrer|referer|came_from|previous_page|origin_url|_orig_referrer|_landing_page|\bref\b|refer(ence|ral|rer)s?)',
        'campaign_tags': r'(utm_source|utm_medium|utm_campaign|utm_term|utm_content|campaign_id|first_utm_parameters|landing_page_params|roistat_.*)',
        'interaction_logging': r'(pageCount|NbPagesVues|pageViewCounter|PageViewEvent|action|activity|events?|interact(ion)?|views?|viewer|homepage|landing)',
    },

    # ===== SECTION 7: STOCKAGE TECHNIQUE ET INFRASTRUCTURE =====
    'INFRASTRUCTURE_AND_STATE': {
        'google_infra': r'(__Secure-[13]PSIDCC|SIDCC|g_state|1P_JAR|NID|firebase_.*|\bfid\b)',
        'load_balancing': r'(AWSALB|AWSALBCORS|AWSESS|SERVERID|AWSELB|AWSELIB|ARRAffinity|BIGipServer|NSC_|TS[a-f0-9]{8})',
        'cdn_routing': r'(akamai|cloudflare|fastly|cdn_|edge_)',
        'state_management': r'^(persist:|redux|root_state|vuex|pinia|app_state|ngrx|store_state|apollo-cache|graphql_cache)',
        'generic_storage': r'(stash|blob|persist|store|cache|localStorage|sessionStorage|LFR_SESSION_STATE_|wzsession|session[0-9]+|__lsv__|indexeddb_.*|idb_.*)',
    },

    # ===== SECTION 8: E-COMMERCE ET SUPPORT CLIENT =====
    'ECOMMERCE_AND_SUPPORT': {
        'cart_and_basket': r'(cart_items|basket_data|shopping_cart|cart_currency|cart_id|basket_id|WC_CartOrderId_)',
        'platform_specific': r'(mage-.*|shopify_.*|_shopify_s|_shopify_y|_shopify_m|secure_customer_sig)',
        'sales_funnel': r'(recently_viewed_product|product_id|sku|RecentProduct|checkout|order_id|sale_id|transaction_id|dwac_|lead_id|conversion_id|signup_date)',
        'support_chats': r'(crisp-client|intercom|ZD-suid|tawkUUID|driftt_|__lc\.|uslk_umm_|LPSID-|giosg_|\bchat\b)',
        'ui_elements': r'(popup|modal|banner|overlay|toast|lightbox|widget|slideout|theme|skin|layout|viewed_popup|dismissed_banner)',
    },

    # ===== SECTION 9: CLÉS ET FORMATS DE DONNÉES SENSIBLES =====
    'DIRECT_PII_KEYS': {
        'identity_keys': r'\b(email|mail|e-mail|e_mail|userEmail|phone|tel|telephone|mobile|cellphone|firstName|last_name|full_name|prenom|givenName|displayName|username|userName)\b',
        'address_keys': r'\b(address|street|adresse|rue|city|ville|zipCode|postal_code|postcode|cp|country|pays)\b',
        'demographic_keys': r'\b(birthDate|dob|birthday|dateNaissance|birthYear|gender|sex|sexe|genre|civilite|age|userAge|latitude|longitude|geoLocation)\b',
        'security_keys': r'\b(password|passwd|pwd|pass|motDePasse|creditCard|cardNumber|cvv|cvc|ssn|social_security|nationalId|taxId)\b',
        'account_keys': r'\b(userId|user_id|customerId|accountId|memberId|clientId|client_id)\b',
        'technical_meta': r'\b(timestamp|created_at|updated_at|last_visit|event_time|session_start)\b',
    },

    'SUSPICIOUS_FORMATS': {
        'data_structures': r'(https?://|https?%3A%2F%2F|^ey[A-Za-z0-9+/]{20,}={0,2}$|^(a:\d+:\{|O:\d+:|s:\d+:)|[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$|jwtToken|__Secure-ROLLOUT_TOKEN|__ktpct)',
    },
    
    'FINGERPRINTING_ADVANCED': {
        'webgl_canvas': r'(webgl_vendor|webgl_renderer|unmasked_vendor|unmasked_renderer|gl_extensions|canvas_winding|canvas_todataurl)',
        'hardware_concurrency': r'(hardware_concurrency|device_memory|cpu_class|platform_ua|font_list|font_hash|audio_fingerprint)',
    }
}