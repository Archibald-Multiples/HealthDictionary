"""
Database initialization script for Healthcare Terminology Dictionary.
This script populates the database with initial categories and healthcare terms
in English and Ewe languages.
"""

import os
import sys
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add parent directory to path so we can import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from app import app, db
    from models import Category, Term
except ImportError as e:
    logger.error(f"Error importing required modules: {e}")
    sys.exit(1)

# Define CATEGORIES and TERMS as Python lists
CATEGORIES = [
    {"id": 1, "name_en": "Body Parts", "name_ewe": "Ŋutilã Ƒe Akpawo", "description_en": "Names and terminology for parts of the human body.", "description_ewe": "Ŋutilã ƒe akpawo ƒe ŋkɔwo kple nyagbɔgblɔwo."},
    {"id": 2, "name_en": "Diseases", "name_ewe": "Dɔvɔ̃wo", "description_en": "Common and notable diseases, illnesses, and conditions.", "description_ewe": "Dɔvɔ̃ dzidzɔwo kple dɔléle siwo amewo dōna."},
    {"id": 3, "name_en": "Symptoms", "name_ewe": "Dɔ Ƒe Dzesiwo", "description_en": "Signs and indications of medical conditions.", "description_ewe": "Dɔléleawo ƒe dzesiwo kple nusi fia be dɔ aɖe le ame ŋu."},
    {"id": 4, "name_en": "Medications", "name_ewe": "Atikevo Vovovowo", "description_en": "Medicines, drugs, and pharmaceutical treatments.", "description_ewe": "Atikevo vovovowo kple gbɔbɔdɔwo ƒe atikɔwo."},
    {"id": 5, "name_en": "Medical Procedures", "name_ewe": "Dɔyɔyɔ Ƒe Mɔnuwo", "description_en": "Common healthcare procedures, tests, and examinations.", "description_ewe": "Dɔyɔyɔ ƒe mɔnu siwo wotsɔna dōa dɔ lãmelélawo."},
    {"id": 6, "name_en": "Medical Equipment", "name_ewe": "Dɔyɔnuwo", "description_en": "Tools, devices, and equipment used in healthcare.", "description_ewe": "Dɔyɔnu siwo wotsɔ dōa dɔ lãmelélawo."}
]

TERMS = [
    {
      "id": 1,
      "term_en": "Heart",
      "term_ewe": "Dzi",
      "definition_en": "The muscular organ that pumps blood through the circulatory system.",
      "definition_ewe": "Ŋutilã ƒe akpa si tua ʋu ɖe ʋudzɔdzɔ me.",
      "example_en": "The doctor listened to my heart with a stethoscope.",
      "example_ewe": "Dɔyɔla la tsɔ ʋu sese nu ɖo toe nye dzi.",
      "category_id": 1
    },
    {
      "id": 2,
      "term_en": "Lung",
      "term_ewe": "Dzime",
      "definition_en": "One of the two organs in the chest that are used for breathing.",
      "definition_ewe": "Akutiwo dome nu evea ɖeka si ŋudɔ wowɔna le gbɔgbɔxexe me.",
      "example_en": "The lungs exchange oxygen and carbon dioxide during respiration.",
      "example_ewe": "Dzime trɔa ya nyui kple ya gbegblẽ le gbɔgbɔxexe me.",
      "category_id": 1
    },
    {
      "id": 3,
      "term_en": "Blood",
      "term_ewe": "Ʋu",
      "definition_en": "The red liquid that circulates in the blood vessels of humans and other vertebrates.",
      "definition_ewe": "Notsi dzĩe si tsana le ʋudzɔdzɔwo me le amegbetɔwo kple lã bubuwo me.",
      "example_en": "The nurse drew blood for testing.",
      "example_ewe": "Dɔyɔla ɖe ʋu be yeado kpɔ.",
      "category_id": 1
    },
    {
      "id": 4,
      "term_en": "Malaria",
      "term_ewe": "Asrã",
      "definition_en": "A disease caused by a plasmodium parasite, transmitted by the bite of infected mosquitoes.",
      "definition_ewe": "Dɔvɔ̃ si nu memee tsɔna aɖoa ame dzi, togodo ƒe aɖuɖu tsɔnɛ vana ame ŋu.",
      "example_en": "He was diagnosed with malaria after returning from his trip.",
      "example_ewe": "Wokpɔe be asrã le eŋu esi wòtrɔ tso mozozo me.",
      "category_id": 2
    },
    {
      "id": 5,
      "term_en": "Diabetes",
      "term_ewe": "Suklidɔ",
      "definition_en": "A disease in which the body's ability to produce or respond to insulin is impaired.",
      "definition_ewe": "Dɔvɔ̃ si nana be ame ƒe lãme metea ŋu wɔa dɔ kple sukli nyuie o.",
      "example_en": "She manages her diabetes with diet and medication.",
      "example_ewe": "Edōa suklidɔ la le nuɖuɖu kple atikevo xɔxɔ me.",
      "category_id": 2
    },
    {
      "id": 6,
      "term_en": "Hypertension",
      "term_ewe": "Ʋusesẽ",
      "definition_en": "Abnormally high blood pressure, especially persistently high arterial blood pressure.",
      "definition_ewe": "Ʋu ƒe sesẽ le ʋudzɔdzɔ me si ƒe agbɔsɔsɔ wui sãa na kuxi.",
      "example_en": "Hypertension can lead to heart disease if left untreated.",
      "example_ewe": "Ʋusesẽ ate ŋu ahe dzidɔ va ne womekpɔ edzi nyuie o.",
      "category_id": 2
    },
    {
      "id": 7,
      "term_en": "Fever",
      "term_ewe": "Dzodzo",
      "definition_en": "An abnormally high body temperature, usually with shivering.",
      "definition_ewe": "Lãme ƒe dzodzo agbɔ, si zɔna kple avuvɔ.",
      "example_en": "The child had a high fever of 102°F.",
      "example_ewe": "Ɖevi la ƒe lãme ƒe dzodzo ɖɔ ŋutɔ.",
      "category_id": 3
    },
    {
      "id": 8,
      "term_en": "Cough",
      "term_ewe": "Kpekpe",
      "definition_en": "A sudden, noisy expulsion of air from the lungs.",
      "definition_ewe": "Ya gbegblẽ ƒe gbidigbidi ado go tso dzime si awɔ ɖe to me.",
      "example_en": "He has had a persistent cough for three weeks.",
      "example_ewe": "Kpekpe le esi ɖaa wòle kɔsiɖa etɔ̃ sɔŋ.",
      "category_id": 3
    },
    {
      "id": 9,
      "term_en": "Pain",
      "term_ewe": "Vevesese",
      "definition_en": "Physical suffering or discomfort caused by illness or injury.",
      "definition_ewe": "Lãme ƒe vevesese si va to dɔléle alo abi me.",
      "example_en": "She experienced severe pain in her lower back.",
      "example_ewe": "Dzime kaŋkaŋ le veve sem nɛ ŋutɔŋutɔ.",
      "category_id": 3
    },
    {
      "id": 10,
      "term_en": "Antibiotic",
      "term_ewe": "Dɔvɔ̃ƒoati",
      "definition_en": "A medicine that inhibits the growth of or destroys microorganisms.",
      "definition_ewe": "Atikevo si wua dɔvɔ̃ me numiemie siwo womate ŋu akpɔ kple ŋku o.",
      "example_en": "The doctor prescribed antibiotics for his bacterial infection.",
      "example_ewe": "Dɔyɔla la na dɔvɔ̃ƒoati be wòano.",
      "category_id": 4
    },
    {
      "id": 11,
      "term_en": "Painkiller",
      "term_ewe": "Vevesedɔati",
      "definition_en": "A drug that relieves pain.",
      "definition_ewe": "Atike si nana vevesese nu dzudzɔna.",
      "example_en": "She took a painkiller for her headache.",
      "example_ewe": "Exɔ vevesedɔati ɖe ta ƒe vevesese ŋu.",
      "category_id": 4
    },
    {
      "id": 12,
      "term_en": "Vaccine",
      "term_ewe": "Tsidɔkanu",
      "definition_en": "A substance used to stimulate the production of antibodies to provide immunity against diseases.",
      "definition_ewe": "Atikevo si wotɔna na amewo be woakpɔ ŋusẽ atsi dɔvɔ̃wo nu.",
      "example_en": "Children should receive the measles vaccine.",
      "example_ewe": "Ele be woaɖe tsidɔkanu na ɖeviwo ɖe sakpate ŋu.",
      "category_id": 4
    },
    {
      "id": 13,
      "term_en": "Surgery",
      "term_ewe": "Lãmedɔwɔwɔ",
      "definition_en": "Medical treatment of injuries or disease involving cutting open the body and removing or repairing damaged parts.",
      "definition_ewe": "Dɔyɔyɔ ƒe mɔnu si wotsɔna lãa ame ƒe lãme aɖe nusiwo gblẽ la ɖa.",
      "example_en": "He needs surgery to remove his appendix.",
      "example_ewe": "Ehiã be woawɔ lãmedɔwɔwɔ nɛ aɖe dɔmenu aɖe le eƒe dɔme.",
      "category_id": 5
    },
    {
      "id": 14,
      "term_en": "Blood Test",
      "term_ewe": "Ʋudokpɔkpɔ",
      "definition_en": "An examination of a sample of blood to determine its composition and to diagnose disease.",
      "definition_ewe": "Ʋu ƒe dodokpɔ si wowɔna be woanya ne dɔvɔ̃ aɖe le ame ŋu.",
      "example_en": "Your blood test results show normal glucose levels.",
      "example_ewe": "Wò ʋudokpɔkpɔ fia be sukli si le wò ʋu me la sɔ pɛpɛpɛ.",
      "category_id": 5
    },
    {
      "id": 15,
      "term_en": "X-ray",
      "term_ewe": "Lãmekpɔfoto",
      "definition_en": "A photographic or digital image of the internal composition of something, especially a part of the body.",
      "definition_ewe": "Foto si woɖena kple mɔ̀ tɔxɛ aɖe si nana woate ŋu akpɔ ame ƒe ŋutilã me.",
      "example_en": "The doctor ordered an X-ray of his broken arm.",
      "example_ewe": "Dɔyɔla la be woaɖe lãmekpɔfoto le eƒe abɔ si ŋe la ŋu.",
      "category_id": 5
    },
    {
      "id": 16,
      "term_en": "Stethoscope",
      "term_ewe": "Ʋusesenu",
      "definition_en": "An instrument used by doctors to listen to sounds within the body, especially the heart and lungs.",
      "definition_ewe": "Dɔyɔnu si dɔyɔlawo tsɔna ɖoa to ʋu kple gbɔgbɔxexe le lãme.",
      "example_en": "The doctor used a stethoscope to listen to her heartbeat.",
      "example_ewe": "Dɔyɔla la tsɔ ʋusesenu ɖo toe eƒe dzi.",
      "category_id": 6
    },
    {
      "id": 17,
      "term_en": "Thermometer",
      "term_ewe": "Lãmedzodzosesenu",
      "definition_en": "An instrument for measuring and indicating temperature.",
      "definition_ewe": "Dɔyɔnu si wotsɔna sesẽa lãme ƒe dzodzo.",
      "example_en": "The nurse used a digital thermometer to check his temperature.",
      "example_ewe": "Dɔyɔlakpɔla la tsɔ lãmedzodzosesenu tɔxe susui ƒe lãme ƒe dzodzo.",
      "category_id": 6
    },
    {
      "id": 18,
      "term_en": "Wheelchair",
      "term_ewe": "Tedziʋu",
      "definition_en": "A chair mounted on wheels for use by people who cannot walk.",
      "definition_ewe": "Zikpui si le afɔtome si dzi ame siwo mate ŋu azɔ o la nɔna.",
      "example_en": "After his accident, he had to use a wheelchair for mobility.",
      "example_ewe": "Le eƒe afɔku megbe la, ele be wòazã tedziʋu hafi ate ŋu aɖe afɔ.",
      "category_id": 6
    },
    {
      "id": 19,
      "term_en": "eyes",
      "term_ewe": "ŋku",
      "definition_en": "The organ of sight",
      "definition_ewe": "Nukpɔnu",
      "example_en": "Check your eyes regularly",
      "example_ewe": "Kpɔ wò ŋkuwo ɖa kabakaba",
      "category_id": 1
    },
    {
      "id": 20,
      "term_en": "ears",
      "term_ewe": "to",
      "definition_en": "The organ of hearing",
      "definition_ewe": "Nuseenu",
      "example_en": "Clean your ears gently",
      "example_ewe": "Klɔ wò towo blewuu",
      "category_id": 1
    },
    {
      "id": 21,
      "term_en": "nose",
      "term_ewe": "ŋɔti",
      "definition_en": "The organ of smell",
      "definition_ewe": "Nuʋeʋẽnu",
      "example_en": "Breathe through your nose",
      "example_ewe": "Gbɔ agbɔ to wò ŋɔti me",
      "category_id": 1
    },
    {
      "id": 22,
      "term_en": "mouth",
      "term_ewe": "nu",
      "definition_en": "The opening for eating and speaking",
      "definition_ewe": "Nuɖuɖu kple nuƒoƒonu",
      "example_en": "Keep your mouth clean",
      "example_ewe": "Na wò nu nanɔ dzadzɛe",
      "category_id": 1
    },
    {
      "id": 23,
      "term_en": "stomach",
      "term_ewe": "fo",
      "definition_en": "The organ that digests food",
      "definition_ewe": "Nu si gblẽa nuɖuɖu",
      "example_en": "My stomach is upset",
      "example_ewe": "Nye fo me le nyam",
      "category_id": 1
    },
    {
      "id": 24,
      "term_en": "diabetes",
      "term_ewe": "suklidɔ",
      "definition_en": "Disease affecting blood sugar",
      "definition_ewe": "Dɔ si kaa sukli le ʋu me",
      "example_en": "Monitor your diabetes daily",
      "example_ewe": "Kpɔ wò suklidɔ ɖa gbe sia gbe",
      "category_id": 2
    },
    {
      "id": 25,
      "term_en": "hypertension",
      "term_ewe": "ʋunyanyra",
      "definition_en": "High blood pressure",
      "definition_ewe": "Ʋu ƒe nyanyram kɔkɔ",
      "example_en": "Control your hypertension",
      "example_ewe": "Ɖu wò ʋunyanyra dzi",
      "category_id": 2
    },
    {
      "id": 26,
      "term_en": "malaria",
      "term_ewe": "ƒodɔ",
      "definition_en": "Disease spread by mosquitoes",
      "definition_ewe": "Dɔ si yitiwo kakana",
      "example_en": "Malaria causes fever",
      "example_ewe": "Ƒodɔ henaa asrã",
      "category_id": 2
    },
    {
      "id": 27,
      "term_en": "tuberculosis",
      "term_ewe": "ƒodo",
      "definition_en": "Lung infection disease",
      "definition_ewe": "Dɔ si kaa ƒodo",
      "example_en": "TB treatment takes months",
      "example_ewe": "Ƒodo ƒe dɔyɔyɔ xɔa ɣleti geɖewo",
      "category_id": 2
    },
    {
      "id": 28,
      "term_en": "asthma",
      "term_ewe": "gbɔgbɔdɔ",
      "definition_en": "Breathing difficulty disease",
      "definition_ewe": "Dɔ si wɔnɛ be gbɔgbɔciɖeɖe sesẽna",
      "example_en": "Use your asthma inhaler",
      "example_ewe": "Zã wò gbɔgbɔdɔ ƒe atike",
      "category_id": 2
    },
    {
      "id": 29,
      "term_en": "nausea",
      "term_ewe": "ɖiɖi",
      "definition_en": "Feeling sick to stomach",
      "definition_ewe": "Susu be yeɖe nu ada",
      "example_en": "I have nausea",
      "example_ewe": "Ɖiɖi le dzinye",
      "category_id": 3
    },
    {
      "id": 30,
      "term_en": "vomiting",
      "term_ewe": "nuɖeɖe",
      "definition_en": "Throwing up food",
      "definition_ewe": "Nuɖuɖu ƒe ɖeɖe",
      "example_en": "Stop eating if vomiting",
      "example_ewe": "Dzudzɔ nuɖuɖu ne èle nu ɖem",
      "category_id": 3
    },
    {
      "id": 31,
      "term_en": "diarrhea",
      "term_ewe": "afɔku",
      "definition_en": "Loose bowel movements",
      "definition_ewe": "Afɔ ƒe kuku",
      "example_en": "Drink fluids for diarrhea",
      "example_ewe": "No tsi ne afɔku le asiwò",
      "category_id": 3
    },
    {
      "id": 32,
      "term_en": "dizziness",
      "term_ewe": "tanyinyi",
      "definition_en": "Feeling unsteady",
      "definition_ewe": "Susu be nu le ɖiɖim",
      "example_en": "Sit down if dizzy",
      "example_ewe": "Nɔ anyi ne tanyinyi le dziwò",
      "category_id": 3
    },
    {
      "id": 33,
      "term_en": "chest pain",
      "term_ewe": "akɔtaveve",
      "definition_en": "Pain in the chest area",
      "definition_ewe": "Vevesese le akɔta",
      "example_en": "Chest pain needs attention",
      "example_ewe": "Akɔtaveve hiã kpɔɖeŋu",
      "category_id": 3
    },
    {
      "id": 34,
      "term_en": "antibiotic",
      "term_ewe": "bakteriawuatike",
      "definition_en": "Medicine that kills bacteria",
      "definition_ewe": "Atike si wua bakteriawo",
      "example_en": "Take all antibiotics prescribed",
      "example_ewe": "Tsɔ bakteriawuatike si wofia wò katã",
      "category_id": 4
    },
    {
      "id": 35,
      "term_en": "painkiller",
      "term_ewe": "vevewuatike",
      "definition_en": "Medicine for pain relief",
      "definition_ewe": "Atike si ɖea vevesese ɖa",
      "example_en": "Use painkillers as directed",
      "example_ewe": "Zã vevewuatike abe ale si woɖoe da ene",
      "category_id": 4
    },
    {
      "id": 36,
      "term_en": "vitamin",
      "term_ewe": "lãmesesẽnuatike",
      "definition_en": "Supplement for health",
      "definition_ewe": "Nu si doa ŋusẽ lãmesesẽ",
      "example_en": "Take vitamins with food",
      "example_ewe": "Tsɔ lãmesesẽnuatike kple nuɖuɖu",
      "category_id": 4
    },
    {
      "id": 37,
      "term_en": "insulin",
      "term_ewe": "sukliɖɔɖɔatike",
      "definition_en": "Medicine for diabetes",
      "definition_ewe": "Atike na suklidɔ",
      "example_en": "Store insulin properly",
      "example_ewe": "Dzra insulin ɖo nyuie",
      "category_id": 4
    },
    {
      "id": 38,
      "term_en": "cough syrup",
      "term_ewe": "ƒedɔatike",
      "definition_en": "Medicine for cough",
      "definition_ewe": "Atike na ƒedɔ",
      "example_en": "Measure cough syrup carefully",
      "example_ewe": "Dzidze ƒedɔatike nyuie",
      "category_id": 4
    },
    {
      "id": 39,
      "term_en": "blood test",
      "term_ewe": "ʋukpɔkpɔ",
      "definition_en": "Testing blood sample",
      "definition_ewe": "Ʋu ƒe dodokpɔ",
      "example_en": "Blood test shows health status",
      "example_ewe": "Ʋukpɔkpɔ ɖea lãmesesẽ ƒe nɔnɔme fiana",
      "category_id": 5
    },
    {
      "id": 40,
      "term_en": "surgery",
      "term_ewe": "amama",
      "definition_en": "Operation using tools",
      "definition_ewe": "Dɔwɔwɔ to dɔwɔnu zazã me",
      "example_en": "Surgery requires anesthesia",
      "example_ewe": "Amama hiã aklãmamlɔatike",
      "category_id": 5
    },
    {
      "id": 41,
      "term_en": "injection",
      "term_ewe": "atikedede",
      "definition_en": "Medicine given with needle",
      "definition_ewe": "Atike nana to atikedeti zazã me",
      "example_en": "Injection may sting briefly",
      "example_ewe": "Atikedede ate ŋu abi vie",
      "category_id": 5
    },
    {
      "id": 42,
      "term_en": "vaccination",
      "term_ewe": "aklãmamlɔatike",
      "definition_en": "Prevention medicine shot",
      "definition_ewe": "Atike si ɖea le dɔ vɔ̃wo nu",
      "example_en": "Get vaccinations on schedule",
      "example_ewe": "Xɔ aklãmamlɔatikewo le woƒe ɣeyiɣi dzi",
      "category_id": 5
    },
    {
      "id": 43,
      "term_en": "stethoscope",
      "term_ewe": "dzi ƒe sesenu",
      "definition_en": "Tool to hear heart and lungs",
      "definition_ewe": "Nu si wotsɔna sea dzi kple ƒodo",
      "example_en": "Doctor uses stethoscope",
      "example_ewe": "Dokta zãa dzi ƒe sesenu",
      "category_id": 6
    },
    {
      "id": 44,
      "term_en": "thermometer",
      "term_ewe": "dzidzɔmedenu",
      "definition_en": "Tool to measure temperature",
      "definition_ewe": "Nu si wotsɔna dzidea dzoxɔxɔ",
      "example_en": "Check fever with thermometer",
      "example_ewe": "Tsɔ dzidzɔmedenu kpɔ asrã",
      "category_id": 6
    },
    {
      "id": 45,
      "term_en": "wheelchair",
      "term_ewe": "amesiametɔ",
      "definition_en": "Chair with wheels for mobility",
      "definition_ewe": "Kplɔ̃ si ŋu gaga le na mɔzɔzɔ",
      "example_en": "Patient needs wheelchair",
      "example_ewe": "Dɔnɔ hiã amesiametɔ",
      "category_id": 6
    },
    {
      "id": 46,
      "term_en": "bandage",
      "term_ewe": "ablablabɔ",
      "definition_en": "Cloth for covering wounds",
      "definition_ewe": "Avɔ si wotsɔna blana abiwo",
      "example_en": "Clean bandage prevents infection",
      "example_ewe": "Ablablabɔ dzadzɛ dea ɖokuibɔ nu",
      "category_id": 6
    },
    {
      "id": 47,
      "term_en": "syringe",
      "term_ewe": "atikededeti",
      "definition_en": "Tool for giving injections",
      "definition_ewe": "Nu si wotsɔna dea atike me",
      "example_en": "Use sterile syringe",
      "example_ewe": "Zã atikededeti dzadzɛ",
      "category_id": 6
    }
  ]


def init_db():
    """Initialize the database with categories and terms."""
    try:
        with app.app_context():
            logger.info("Dropping and recreating all tables...")
            db.drop_all()
            db.create_all()

            # Add categories
            logger.info("Adding categories...")
            category_id_set = set()
            for category_data in CATEGORIES:
                category = Category(
                    name_en=category_data["name_en"],
                    name_ewe=category_data["name_ewe"],
                    description_en=category_data["description_en"],
                    description_ewe=category_data["description_ewe"]
                )
                db.session.add(category)
                db.session.flush()  # To get the ID
                category_id_set.add(category.id)

            db.session.commit()
            logger.info(f"Added {len(CATEGORIES)} categories successfully.")

            # Add terms
            logger.info("Adding healthcare terms...")
            now = datetime.utcnow()
            for term_data in TERMS:
                # Use category_id directly from the term data
                if term_data["category_id"] not in category_id_set:
                    logger.warning(f"Category ID '{term_data['category_id']}' not found, skipping term '{term_data['term_en']}'")
                    continue

                term = Term(
                    term_en=term_data["term_en"],
                    term_ewe=term_data["term_ewe"],
                    definition_en=term_data["definition_en"],
                    definition_ewe=term_data["definition_ewe"],
                    example_en=term_data.get("example_en"),
                    example_ewe=term_data.get("example_ewe"),
                    pronunciation=term_data.get("pronunciation"),
                    category_id=term_data["category_id"],
                    created_at=now,
                    updated_at=now
                )
                db.session.add(term)

            db.session.commit()
            logger.info(f"Added {len(TERMS)} healthcare terms successfully.")
            logger.info("Database initialization completed successfully!")

    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        db.session.rollback()
        sys.exit(1)

if __name__ == "__main__":
    init_db()
