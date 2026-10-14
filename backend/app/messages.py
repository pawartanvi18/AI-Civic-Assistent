DEFAULT_LANG = "en"

MESSAGES: dict[str, dict[str, str]] = {
    "en": {
        "disclaimer": (
            "This is an independent guidance tool. It is NOT an official service of "
            "the Brihanmumbai Municipal Corporation or any government body. It does not "
            "submit complaints on your behalf. Always confirm information and submit "
            "complaints through official channels."
        ),
        "ans_one": 'For "{name}", the official place to go is: {authority}. Please use the official link below.',
        "ans_many": "These official services may match your question. Please pick the one you need:\n{list}",
        "fees_note": "Fees, required documents and time limits can change, so please confirm them on the official page.",
        "state_note": "This is a Maharashtra state government service, not a BMC service.",
        "unverified_note": "Note: this link has not been checked yet by the project team. Please confirm it on the official website.",
        "step_1": "Open the official link below.",
        "step_2": "Look for the service named above and follow the instructions shown there.",
        "step_3": "After applying, keep your documents and any reference number safe.",
        "ans_complaint": "This looks like a civic problem ({category}). I can help you prepare a complaint draft. Please tell me the exact location.",
        "ans_insufficient": "I could not verify an answer to this from the official sources I have. Please check the official channel below.",
        "ans_unsupported": "I can't help with that yet. I can help with: {topics}.",
        "q_description": "Could you describe the problem in a bit more detail? For example: garbage, pothole, blocked drain, water supply or streetlight.",
        "q_location": "Where is the problem? Please give the area, street or nearest landmark.",
        "d_to": "To the concerned Ward Office / Department,",
        "d_intro": "I would like to report the following issue:",
        "d_location": "Location: {location}",
        "d_landmark": "Nearby landmark: {landmark}",
        "d_request": "I request that this be looked into and appropriate action taken.",
        "d_footer": "This text was prepared with an independent tool and has not been submitted anywhere.",
        "d_title": "Complaint: {category} at {location}",
        "ns_1": "Review the draft and edit anything that is not correct.",
        "ns_2": "Send it through the official channel shown (WhatsApp, helpline or website).",
        "ns_3": "Ask for a complaint reference number and write it down.",
        "ns_4": "This tool has not submitted anything. Your complaint is registered only after you submit it through an official channel.",
        "ch_phone": "Call {contact}.",
        "ch_whatsapp": "Send a WhatsApp message to {contact}.",
        "ch_web": "Open {url}.",
        "unverified_tag": " (not yet verified)",
    },
    "mr": {
        "disclaimer": (
            "हे एक स्वतंत्र मार्गदर्शन साधन आहे. ही बृहन्मुंबई महानगरपालिका (BMC) किंवा "
            "कोणत्याही सरकारी संस्थेची अधिकृत सेवा नाही. हे तुमच्या वतीने तक्रार दाखल करत नाही. "
            "माहितीची खात्री आणि तक्रार नोंदणी नेहमी अधिकृत माध्यमातूनच करा."
        ),
        "ans_one": '"{name}" साठी अधिकृत ठिकाण: {authority}. कृपया खालील अधिकृत दुवा वापरा.',
        "ans_many": "तुमच्या प्रश्नाशी जुळणाऱ्या अधिकृत सेवा खाली आहेत. तुम्हाला हवी ती निवडा:\n{list}",
        "fees_note": "शुल्क, आवश्यक कागदपत्रे आणि कालमर्यादा बदलू शकतात, म्हणून ती अधिकृत पानावर तपासा.",
        "state_note": "ही महाराष्ट्र राज्य सरकारची सेवा आहे, BMC ची नाही.",
        "unverified_note": "टीप: हा दुवा प्रकल्प टीमने अजून तपासलेला नाही. कृपया अधिकृत संकेतस्थळावर खात्री करा.",
        "step_1": "खालील अधिकृत दुवा उघडा.",
        "step_2": "वर नमूद केलेली सेवा शोधा आणि तिथे दिलेल्या सूचनांचे पालन करा.",
        "step_3": "अर्ज केल्यानंतर तुमची कागदपत्रे आणि संदर्भ क्रमांक सुरक्षित ठेवा.",
        "ans_complaint": "ही नागरी समस्या ({category}) वाटते. मी तुम्हाला तक्रारीचा मसुदा तयार करण्यात मदत करू शकतो. कृपया नेमके ठिकाण सांगा.",
        "ans_insufficient": "अधिकृत स्रोतांमधून मी याची खात्री करू शकलो नाही. कृपया खाली दिलेल्या अधिकृत माध्यमाशी संपर्क साधा.",
        "ans_unsupported": "यासाठी मी अजून मदत करू शकत नाही. मी या विषयांमध्ये मदत करू शकतो: {topics}.",
        "q_description": "कृपया समस्येचे थोडे अधिक तपशीलवार वर्णन करा. उदा. कचरा, खड्डा, तुंबलेली गटार, पाणीपुरवठा किंवा पथदिवा.",
        "q_location": "समस्या कुठे आहे? कृपया परिसर, रस्ता किंवा जवळची खूण सांगा.",
        "d_to": "संबंधित वॉर्ड कार्यालय / विभागास,",
        "d_intro": "मी खालील समस्येची तक्रार करू इच्छितो/इच्छिते:",
        "d_location": "ठिकाण: {location}",
        "d_landmark": "जवळची खूण: {landmark}",
        "d_request": "कृपया या समस्येची दखल घेऊन योग्य ती कारवाई करावी, ही विनंती.",
        "d_footer": "हा मजकूर स्वतंत्र साधनाच्या मदतीने तयार केला आहे आणि कुठेही सादर केलेला नाही.",
        "d_title": "तक्रार: {category}, {location}",
        "ns_1": "मसुदा तपासा आणि चुकीचे असेल ते बदला.",
        "ns_2": "खाली दाखवलेल्या अधिकृत माध्यमातून (WhatsApp, हेल्पलाइन किंवा संकेतस्थळ) तो पाठवा.",
        "ns_3": "तक्रार क्रमांक मागून तो लिहून ठेवा.",
        "ns_4": "या साधनाने काहीही सादर केलेले नाही. तुम्ही अधिकृत माध्यमातून पाठवल्यावरच तक्रार नोंदली जाते.",
        "ch_phone": "{contact} यावर कॉल करा.",
        "ch_whatsapp": "{contact} वर WhatsApp संदेश पाठवा.",
        "ch_web": "{url} उघडा.",
        "unverified_tag": " (अजून तपासलेले नाही)",
    },
    "hi": {
        "disclaimer": (
            "यह एक स्वतंत्र मार्गदर्शन उपकरण है। यह बृहन्मुंबई महानगरपालिका (BMC) या किसी "
            "सरकारी संस्था की आधिकारिक सेवा नहीं है। यह आपकी ओर से शिकायत दर्ज नहीं करता। "
            "जानकारी की पुष्टि और शिकायत हमेशा आधिकारिक माध्यमों से ही करें।"
        ),
        "ans_one": '"{name}" के लिए आधिकारिक स्थान: {authority}। कृपया नीचे दिया गया आधिकारिक लिंक उपयोग करें।',
        "ans_many": "आपके प्रश्न से मेल खाने वाली आधिकारिक सेवाएँ नीचे हैं। अपनी ज़रूरत की सेवा चुनें:\n{list}",
        "fees_note": "शुल्क, आवश्यक दस्तावेज़ और समय-सीमा बदल सकते हैं, इसलिए कृपया उन्हें आधिकारिक पेज पर जाँचें।",
        "state_note": "यह महाराष्ट्र राज्य सरकार की सेवा है, BMC की नहीं।",
        "unverified_note": "ध्यान दें: इस लिंक की जाँच प्रोजेक्ट टीम ने अभी नहीं की है। कृपया आधिकारिक वेबसाइट पर पुष्टि करें।",
        "step_1": "नीचे दिया गया आधिकारिक लिंक खोलें।",
        "step_2": "ऊपर बताई गई सेवा खोजें और वहाँ दिए निर्देशों का पालन करें।",
        "step_3": "आवेदन के बाद अपने दस्तावेज़ और संदर्भ संख्या सुरक्षित रखें।",
        "ans_complaint": "यह एक नागरिक समस्या ({category}) लगती है। मैं शिकायत का मसौदा तैयार करने में आपकी मदद कर सकता हूँ। कृपया सही स्थान बताएँ।",
        "ans_insufficient": "आधिकारिक स्रोतों से मैं इसकी पुष्टि नहीं कर सका। कृपया नीचे दिए गए आधिकारिक माध्यम से संपर्क करें।",
        "ans_unsupported": "इसमें मैं अभी मदद नहीं कर सकता। मैं इन विषयों में मदद कर सकता हूँ: {topics}।",
        "q_description": "कृपया समस्या का थोड़ा और विवरण दें। जैसे: कचरा, गड्ढा, जाम नाली, पानी की आपूर्ति या स्ट्रीटलाइट।",
        "q_location": "समस्या कहाँ है? कृपया इलाका, सड़क या नज़दीकी पहचान स्थल बताएँ।",
        "d_to": "संबंधित वार्ड कार्यालय / विभाग को,",
        "d_intro": "मैं निम्नलिखित समस्या की शिकायत करना चाहता/चाहती हूँ:",
        "d_location": "स्थान: {location}",
        "d_landmark": "नज़दीकी पहचान स्थल: {landmark}",
        "d_request": "कृपया इस समस्या पर ध्यान देकर उचित कार्रवाई करें, यह अनुरोध है।",
        "d_footer": "यह पाठ एक स्वतंत्र उपकरण की मदद से तैयार किया गया है और कहीं भी जमा नहीं किया गया है।",
        "d_title": "शिकायत: {category}, {location}",
        "ns_1": "मसौदा जाँचें और जो सही न हो उसे बदलें।",
        "ns_2": "नीचे दिखाए गए आधिकारिक माध्यम (WhatsApp, हेल्पलाइन या वेबसाइट) से इसे भेजें।",
        "ns_3": "शिकायत संख्या माँगें और उसे लिख लें।",
        "ns_4": "इस उपकरण ने कुछ भी जमा नहीं किया है। आधिकारिक माध्यम से भेजने के बाद ही आपकी शिकायत दर्ज होती है।",
        "ch_phone": "{contact} पर कॉल करें।",
        "ch_whatsapp": "{contact} पर WhatsApp संदेश भेजें।",
        "ch_web": "{url} खोलें।",
        "unverified_tag": " (अभी जाँचा नहीं गया)",
    },
}


def normalize_lang(lang: str | None) -> str:
    return lang if lang in MESSAGES else DEFAULT_LANG


def t(lang: str | None, key: str, **kwargs: str) -> str:
    table = MESSAGES.get(lang or DEFAULT_LANG, MESSAGES[DEFAULT_LANG])
    text = table.get(key) or MESSAGES[DEFAULT_LANG][key]
    return text.format(**kwargs) if kwargs else text