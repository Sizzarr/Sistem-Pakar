# Default seed data copied from the provided knowledge base.
DISEASES = {
    "P01": {
        "name": "Insomnia",
        "description": "Gangguan tidur yang ditandai dengan kesulitan untuk memulai tidur, mempertahankan tidur, atau bangun terlalu awal.",
        "priority": 10,
    },
    "P02": {
        "name": "Sleep Apnea",
        "description": "Gangguan di mana saluran napas tersumbat sebagian atau seluruhnya selama tidur (henti napas).",
        "priority": 20,
    },
    "P03": {
        "name": "Narcolepsy",
        "description": "Rasa kantuk berlebihan di siang hari dan serangan tidur mendadak.",
        "priority": 30,
    },
    "P04": {
        "name": "Restless Leg Syndrome",
        "description": "Sensasi tidak nyaman pada kaki saat akan tidur yang membuat sulit tidur.",
        "priority": 40,
    },
    "P05": {
        "name": "Gangguan Tidur akibat Stres",
        "description": "Kesulitan tidur akibat tekanan psikologis, biasanya akibat stres akademis.",
        "priority": 50,
    },
}

SYMPTOMS = {
    "G01": "Sulit untuk tidur atau sering terbangun di malam hari",
    "G02": "Merasa kelelahan atau kurang energi di siang hari",
    "G03": "Sulit tidur di malam hari meskipun sangat lelah",
    "G04": "Terbangun dengan detak jantung yang cepat atau rasa cemas",
    "G05": "Tidak merasa segar meskipun telah tidur cukup lama",
    "G06": "Mendengkur keras atau sesak nafas saat tidur",
    "G07": "Merasa nafas tersengal-sengal saat bangun tidur",
    "G08": "Terbangun dengan rasa tersedak atau sesak nafas",
    "G09": "Mendengkur keras dengan jeda nafas panjang",
    "G10": "Merasa kantuk berlebihan di siang hari meskipun cukup tidur",
    "G11": "Tertidur mendadak tanpa disadari di siang hari",
    "G12": "Kesulitan untuk tetap terjaga saat melakukan aktivitas",
    "G13": "Mengalami gangguan penglihatan saat merasa kantuk",
    "G14": "Kelumpuhan tidur, yaitu tidak bisa bergerak saat bangun atau sebelum tidur",
    "G15": "Merasa kantuk berlebihan di siang hari meskipun cukup tidur",
    "G16": "Mengalami sensasi tidak nyaman pada kaki saat tidur",
    "G17": "Merasa kesemutan atau ada dorongan untuk menggerakkan kaki saat tidur",
    "G18": "Sering merasa kaki pegal atau berat di malam hari",
    "G19": "Sering meregangkan kaki secara tidak sadar saat tidur",
    "G20": "Mengalami gangguan tidur karena kaki yang sering bergerak",
    "G21": "Sulit berkonsentrasi atau fokus di siang hari",
    "G22": "Mengalami perubahan suasana hati yang ekstrem di siang hari",
    "G23": "Sering merasa marah atau mudah tersinggung di siang hari",
    "G24": "Terbangun tiba-tiba dengan rasa cemas",
    "G25": "Merasa sulit tidur meskipun kondisi lingkungan mendukung",
}

RULES = {
    "P01": ["G01", "G02", "G03", "G04", "G05"],
    "P02": ["G01", "G06", "G07", "G08", "G09", "G10"],
    "P03": ["G01", "G11", "G12", "G13", "G14", "G15"],
    "P04": ["G16", "G17", "G18", "G19", "G20"],
    "P05": ["G21", "G22", "G23", "G24", "G25"],
}
