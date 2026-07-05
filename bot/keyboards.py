"""
Telegram bot keyboards
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton


def get_main_keyboard():
    """
    Get main menu keyboard
    """
    return ReplyKeyboardMarkup([
        [KeyboardButton('/today'), KeyboardButton('/top')],
        [KeyboardButton('/cyber'), KeyboardButton('/software')],
        [KeyboardButton('/abuja'), KeyboardButton('/lagos')],
        [KeyboardButton('/kaduna'), KeyboardButton('/kano')],
        [KeyboardButton('/remote'), KeyboardButton('/stipend')],
        [KeyboardButton('/help')]
    ], resize_keyboard=True)


def get_location_keyboard():
    """
    Get location selection keyboard
    """
    buttons = [
        [InlineKeyboardButton('Abuja', callback_data='location_abuja'),
         InlineKeyboardButton('Lagos', callback_data='location_lagos')],
        [InlineKeyboardButton('Kaduna', callback_data='location_kaduna'),
         InlineKeyboardButton('Kano', callback_data='location_kano')],
        [InlineKeyboardButton('Remote', callback_data='location_remote')]
    ]
    return InlineKeyboardMarkup(buttons)


def get_role_keyboard():
    """
    Get role selection keyboard
    """
    buttons = [
        [InlineKeyboardButton('Software Engineering', callback_data='role_software'),
         InlineKeyboardButton('Cybersecurity', callback_data='role_cyber')],
        [InlineKeyboardButton('Data Analysis', callback_data='role_data'),
         InlineKeyboardButton('Networking', callback_data='role_network')],
        [InlineKeyboardButton('Back', callback_data='menu_back')]
    ]
    return InlineKeyboardMarkup(buttons)
