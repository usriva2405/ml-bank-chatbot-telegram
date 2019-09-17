from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, InlineQueryHandler, MessageHandler, Filters,
                          ConversationHandler)

import requests
import re
import logging
import configparser

import sys, os
sys.path.insert(0, os.path.abspath('..'))

# Custom Modules
from bankchat_app import BankApp


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
bankchat_app = BankApp()

QUERY, CANCEL = range(2)

def initialize():
    bankchat_app = BankApp()


def start(update, context):
    user = update.message.from_user
    update.message.reply_text(
        'Hi {0}! I am your bank bot. '
        'Send /cancel to stop talking to me.\n\n'
        'How can I help you regarding your account?' 
        '\nBalance? History? Card Block? Anything else?'.format(user.first_name))
    
    return QUERY

def closing_statement(text):
    closing_words = re.compile("thank|Thank|no|No|thats|Thats|Thanks") 
    if closing_words.search(text): return True
    else: return False


def query(update, context):
    user = update.message.from_user
    text = update.message.text
    if closing_statement(text) == True:
        logger.info("closing_statement = true %s: %s", user.first_name, update.message.text)
        #answer, answer_cat, question_cat = bankchat_app.predict_answer(text)
        answer = bankchat_app.predict_answer(text)
        update.message.reply_text(answer)
        return CANCEL
    else:
        #predict resposne
        #answer, answer_cat, question_cat = bankchat_app.predict_answer(text)
        answer = bankchat_app.predict_answer(text)
        answer_category = bankchat_app.predict_answer_category(text)
        question_category = bankchat_app.predict_question_category(text)
        logger.info('************************')
        logger.info('Prediction given by model')
        logger.info('************************')
        logger.info("answer : {0}".format(answer))
        logger.info("answer category : {0}".format(answer_category))
        logger.info("ques category : {0}".format(question_category))
        
        
        response = answer + '\n\n Can I help you with anything else?'
        
        logger.info("Query %s: %s", user.first_name, update.message.text)
        update.message.reply_text(response)
    
        return QUERY
    
def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! Happy to help!!',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END

    
def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)



def main():
    
    initialize();
    # Read telegram token from config
    config = configparser.ConfigParser()
    config.read('config.ini')
    telegram_token = config['telegram']['telegram-token']
    #telegram_token = config['telegram-token']
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(telegram_token, use_context=True)
    dp = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            QUERY: [MessageHandler(Filters.text, query)],
            CANCEL: [CommandHandler('cancel', cancel)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        allow_reentry=True
    )
    dp.add_handler(conv_handler)
    # log all errors
    dp.add_error_handler(error)
    
    updater.start_polling()
    updater.idle()



if __name__ == '__main__':

    main()
