import os
import logging

# ----- Phase 1: Project Setup & Planning -----
# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID', 'vKR78V_JKDoJVsmfvlQaUw')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET', 'Thmlm0y2-fu4rGAdKuRdHOZ4-1803w')
REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT', 'windows:ShujaScript2:0.1 (by /u/Weary_Willow_168)')

logging.info("Project setup complete. Reddit credentials loaded.")