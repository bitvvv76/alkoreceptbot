import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
    )
# загружаем .env
load_dotenv()

# получаем токен
BOT_TOKEN = os.getenv("BOT_TOKEN")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ADMIN_ID = 7815792058

users = set()
logs = []
USERS_FILE = "users.json"

def load_users():
    global users

    try:
        with open(USERS_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
            users = set(data)
    except FileNotFoundError:
        users = set()
    except json.JSONDecodeError:
        users = set()


def save_users():
    with open(USERS_FILE, "w", encoding="utf-8") as file:
        json.dump(list(users), file, ensure_ascii=False, indent=2)


client = OpenAI(api_key=OPENAI_API_KEY)

classic_recipes = {
    "🍋 Лимончелло": (
        "🍋 Лимончелло\n\n"
        "Ингредиенты:\n"
        "• водка 40% — 500 мл\n"
        "• цедра лимона — 4–5 шт\n"
        "• сахар — 200–300 г\n"
        "• вода — 200 мл\n\n"
        "Срок настаивания: 7–10 дней.\n"
        "После настаивания: процедить, добавить сироп, охладить.\n\n"
        "18+ Ответственное употребление."
    ),

    "🍒 Вишнёвая": (
        "🍒 Вишнёвая настойка\n\n"
        "Ингредиенты:\n"
        "• вишня — 500 г\n"
        "• водка 40% — 500 мл\n"
        "• сахар — 150–250 г\n\n"
        "Срок настаивания: 2–4 недели.\n"
        "Совет: периодически встряхивать банку.\n\n"
        "18+ Ответственное употребление."
    ),

    "🌿 Хреновуха": (
        "🌿 Хреновуха\n\n"
        "Ингредиенты:\n"
        "• водка 40% — 500 мл\n"
        "• хрен — 30–50 г\n"
        "• мёд — 1 ч.л.\n"
        "• лимонный сок — 1 ч.л.\n\n"
        "Срок настаивания: 3–5 дней.\n"
        "Важно: не передерживать, чтобы не было сильной горечи.\n\n"
        "18+ Ответственное употребление."
    ),
    
    "❤️ Клюковка": (
        "❤️ Клюковка\n\n"
        "Ингредиенты:\n"
        "• клюква — 400–500 г\n"
        "• водка 40% — 500 мл\n"
        "• мёд или сахар — по вкусу\n\n"
        "Срок настаивания: 10–14 дней.\n"
        "Совет: слегка размять ягоды перед настаиванием.\n\n"
        "18+ Ответственное употребление."
    ),

    "🍏 Яблочная с корицей": (
        "🍏 Яблочная с корицей\n\n"
        "Ингредиенты:\n"
        "• яблоки — 2–3 шт\n"
        "• водка 40% — 500 мл\n"
        "• палочка корицы — 1 шт\n"
        "• мёд — по вкусу\n\n"
        "Срок настаивания: 7–10 дней.\n"
        "Совет: использовать сладкие ароматные яблоки.\n\n"
        "18+ Ответственное употребление."
    ),

    "☕ Кофейная": (
        "☕ Кофейная настойка\n\n"
        "Ингредиенты:\n"
        "• кофе в зернах — 50 г\n"
        "• водка 40% — 500 мл\n"
        "• ваниль — по желанию\n"
        "• сахар или сироп — по вкусу\n\n"
        "Срок настаивания: 5–7 дней.\n"
        "Совет: использовать свежеобжаренный кофе.\n\n"
        "18+ Ответственное употребление."
    ),
}

sous_vide_recipes = {
    "🔥🍋 Су-вид лимончелло": (
        "🔥🍋 Су-вид лимончелло\n\n"
        "Ингредиенты:\n"
        "• водка 40% — 500 мл\n"
        "• цедра лимона — 4–5 шт\n"
        "• сахарный сироп — по вкусу\n\n"
        "Температура: 55°C\n"
        "Время: 2 часа\n\n"
        "После приготовления: охладить, процедить, дать отдохнуть 1–3 дня.\n\n"
        "Важно: использовать герметичный пакет/банку, не перегревать алкоголь.\n\n"
        "18+ Ответственное употребление."
    ),

    "🔥🍒 Су-вид вишнёвая": (
        "🔥🍒 Су-вид вишнёвая\n\n"
        "Ингредиенты:\n"
        "• вишня — 400 г\n"
        "• водка 40% — 500 мл\n"
        "• сахар — 100–150 г\n\n"
        "Температура: 60°C\n"
        "Время: 2–3 часа\n\n"
        "После приготовления: процедить и выдержать 2–5 дней.\n\n"
        "Важно: не нагревать выше 60°C.\n\n"
        "18+ Ответственное употребление."
    ),

    "🔥🌶 Су-вид перцовка": (
        "🔥🌶 Су-вид перцовка\n\n"
        "Ингредиенты:\n"
        "• водка 40% — 500 мл\n"
        "• перец чили — маленький кусочек\n"
        "• мёд — 1 ч.л.\n"
        "• душистый перец — 2–3 горошины\n\n"
        "Температура: 50–55°C\n"
        "Время: 1–2 часа\n\n"
        "Совет: перец лучше добавлять осторожно, чтобы не сделать напиток слишком жгучим.\n\n"
        "18+ Ответственное употребление."
    ),

    
    "🔥❤️ Су-вид клюковка": (
        "🔥❤️ Су-вид клюковка\n\n"
        "Ингредиенты:\n"
        "• клюква — 400 г\n"
        "• водка 40% — 500 мл\n"
        "• сахар или мёд — по вкусу\n\n"
        "Температура: 55–60°C\n"
        "Время: 2 часа\n\n"
        "После приготовления: охладить, процедить, дать отдохнуть 1–2 дня.\n\n"
        "18+ Ответственное употребление."
    ),

    "🔥🍏 Су-вид яблочная с корицей": (
        "🔥🍏 Су-вид яблочная с корицей\n\n"
        "Ингредиенты:\n"
        "• яблоки — 2–3 шт\n"
        "• водка 40% — 500 мл\n"
        "• палочка корицы — 1 шт\n"
        "• мёд — по вкусу\n\n"
        "Температура: 55°C\n"
        "Время: 2 часа\n\n"
        "После приготовления: охладить, процедить, дать отдохнуть 1–3 дня.\n\n"
        "18+ Ответственное употребление."
    ),

    "🔥☕ Су-вид кофейная": (
        "🔥☕ Су-вид кофейная\n\n"
        "Ингредиенты:\n"
        "• кофе в зернах — 40–50 г\n"
        "• водка 40% — 500 мл\n"
        "• ваниль — по желанию\n"
        "• сахарный сироп — по вкусу\n\n"
        "Температура: 50–55°C\n"
        "Время: 1–2 часа\n\n"
        "После приготовления: процедить через фильтр и дать отдохнуть 1–2 дня.\n\n"
        "18+ Ответственное употребление."
    ),
}

cocktail_recipes = {
    "🍊 Цитрусовая для коктейлей": (
        "🍊 Цитрусовая для коктейлей\n\n"
        "🍸 Подходит для:\n"
        "• Old Fashioned\n"
        "• Negroni\n"
        "• Whiskey Sour\n\n"
        "🥃 Основа:\n"
        "• бурбон или джин — 500 мл\n\n"
        "🍊 Ингредиенты:\n"
        "• цедра апельсина — 1 шт\n"
        "• цедра лимона — 1 шт\n"
        "• мёд или сироп — по вкусу\n\n"
        "⏳ Настаивание: 5–7 дней.\n\n"
        "❤️ Вкус: яркий, цитрусовый, барный.\n\n"
        "18+ Ответственное употребление."
    ),

    "☕ Кофейная для Espresso Martini": (
        "☕ Кофейная для Espresso Martini\n\n"
        "🍸 Подходит для:\n"
        "• Espresso Martini\n"
        "• White Russian\n"
        "• кофейных твистов\n\n"
        "🥃 Основа:\n"
        "• водка или ром — 500 мл\n\n"
        "☕ Ингредиенты:\n"
        "• кофе в зёрнах — 40 г\n"
        "• ваниль — по желанию\n"
        "• сахарный сироп — по вкусу\n\n"
        "⏳ Настаивание: 5–7 дней.\n\n"
        "❤️ Вкус: кофейный, насыщенный, мягкий.\n\n"
        "18+ Ответственное употребление."
    ),

    "🍒 Вишнёвая для Manhattan": (
        "🍒 Вишнёвая для Manhattan\n\n"
        "🍸 Подходит для:\n"
        "• Manhattan\n"
        "• Boulevardier\n"
        "• Whiskey Sour\n\n"

        "🥃 Основа:\n"
        "• бурбон — 500 мл\n\n"

        "🍒 Ингредиенты:\n"
        "• вишня — 200 г\n"
        "• ваниль — по желанию\n"
        "• сахар — 1-2 ст. л.\n\n"

        "⏳ Настаивание: 7–10 дней.\n\n"

        "❤️ Вкус: ягодный, насыщенный, бархатистый.\n\n"

        "18+ Ответственное употребление."
    ),

    "🌿 Мятная для Mojito": (
        "🌿 Мятная для Mojito\n\n"
        "🍸 Подходит для:\n"
        "• Mojito\n"
        "• Mint Julep\n"
        "• летних коктейлей\n\n"

        "🥃 Основа:\n"
        "• белый ром — 500 мл\n\n"

        "🌿 Ингредиенты:\n"
        "• свежая мята — большой пучок\n"
        "• лаймовая цедра — немного\n"
        "• сироп — по вкусу\n\n"

        "⏳ Настаивание: 3–5 дней.\n\n"

        "❤️ Вкус: свежий, холодный, ярко-мятный.\n\n"

        "18+ Ответственное употребление."
    ),

    "🌶 Пряная для Bloody Mary": (
        "🌶 Пряная для Bloody Mary\n\n"
        "🍸 Подходит для:\n"
        "• Bloody Mary\n"
        "• пряных коктейлей\n\n"

        "🥃 Основа:\n"
        "• водка — 500 мл\n\n"

        "🌶 Ингредиенты:\n"
        "• чили — маленький кусочек\n"
        "• чёрный перец — 5 горошин\n"
        "• копчёная паприка — щепотка\n\n"

        "⏳ Настаивание: 2–4 дня.\n\n"

        "❤️ Вкус: острый, пряный, согревающий.\n\n"

        "18+ Ответственное употребление."
    ),
}

def get_main_menu():

    keyboard = [
    ["📖 Классические настойки", "🔥 Настойки су-вид"],
    ["🥃 Коктейльные настойки", "🧪 Craft Spirits"],
    ["🍸 AI бармен"],
    ["ℹ️ Помощь"]
]


    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    if user_id != ADMIN_ID:
        await update.message.reply_text(
            "⛔ Доступ запрещён."
        )
        return

    keyboard = [
        ["👥 Пользователи", "📊 Статистика"],
        ["📢 Рассылка", "📝 Логи"],
        ["⬅️ Назад"]
    ]

    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )

    await update.message.reply_text(
        "🔐 Админ-панель\n\n"
        "Выбери раздел:",
        reply_markup=reply_markup
    )
async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["support_mode"] = True

    await update.message.reply_text(
        "🆘 Поддержка\n\n"
        "Опишите проблему, вопрос или предложение одним сообщением.\n\n"
        "Сообщение будет отправлено администратору."
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        ["📖 Классические настойки"],
        ["🔥 Настойки су-вид"],
        ["ℹ️ Помощь"]
    ]

    users.add(update.effective_user.id)
    save_users()

    reply_markup = get_main_menu()

    await update.message.reply_text(
        "Привет 🍸\n\n"
        "Я бот alkorecept.\n"
        "Помогаю с классическими настойками и настойками су-вид 🔥",
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text
    user_id = update.effective_user.id

    logs.append(f"{user_id}: {text}")

    if len(logs) > 20:
        logs.pop(0)

    support_mode = context.user_data.get("support_mode")

    if support_mode:

        context.user_data["support_mode"] = False

        user_id = update.effective_user.id
        username = update.effective_user.username

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=(
                "🆘 SUPPORT\n\n"
                f"👤 User ID: {user_id}\n"
                f"🔗 Username: @{username}\n\n"
                f"Сообщение:\n{text}"
            )
        )

        await update.message.reply_text(
            "✅ Сообщение отправлено администратору.\n\n"
            "Спасибо за обратную связь!"
        )

        return
    
    admin_mode = context.user_data.get("admin_mode")

    if admin_mode == "broadcast":

        if update.effective_user.id != ADMIN_ID:
            return

        context.user_data["admin_mode"] = None

        success = 0

        for user in users:
            try:
                await context.bot.send_message(
                    chat_id=user,
                    text=f"📢 Сообщение от AI бармена\n\n{text}"
                )
                success += 1
            except:
                pass

        await update.message.reply_text(
            f"✅ Рассылка отправлена.\n\n"
            f"Получили: {success}"
        )
        return

    button_texts = {
        "📖 Классические настойки",
        "🔥 Настойки су-вид",
        "🥃 Коктейльные настойки",
        "🍸 AI коктейль",
        "🍸 AI бармен",
        "ℹ️ Помощь",
        "⬅️ Назад",

        "📋 Рецепты",
        "🤖 ИИ-рецепт",
        "🔥📋 Су-вид рецепты",
        "🔥🤖 ИИ су-вид рецепт",
        "📋 Барные рецепты",
        "🤖 ИИ барный рецепт",

        "🧪 Craft Spirits",
        "🥃 В стиле виски",
        "🌿 В стиле джина",
        "🌵 В стиле текилы",
        "🍹 В стиле рома",
        "🤖 AI craft recipe",

        "🔎 По названию настойки",
        "🧺 По ингредиентам настойки",
        "🔎 По названию су-вид настойки",
        "🧺 По ингредиентам су-вид",
        "🔎 По названию барной настойки",
        "🧺 По ингредиентам барной настойки",
        "🔥 Су-вид барная настойка",
        "🔎 По названию коктейля",
        "🧺 По ингредиентам",
    }

    if text in button_texts:
        context.user_data["ai_mode"] = None

    ai_mode = context.user_data.get("ai_mode")

    if ai_mode == "classic":

        context.user_data["ai_mode"] = None

        await update.message.reply_text("🤖 Думаю над рецептом...")

        response = client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {
                    "role": "system",
                    "content": (
                        "Ты бармен и эксперт по домашним настойкам 18+.\n\n"

                        "Пиши рецепты ТОЛЬКО в таком Telegram-стиле:\n\n"

                        "🍒 Название настойки\n\n"

                        "🥃 Основа:\n"
                        "• водка — количество\n\n"

                        "🍓 Ингредиенты:\n"
                        "• ингредиент\n"
                        "• ингредиент\n\n"

                        "⏳ Настаивание:\n"
                        "• сроки\n\n"

                        "🧪 Как готовить:\n"
                        "• короткие шаги\n\n"

                        "❤️ Вкус:\n"
                        "• краткое описание вкуса\n\n"

                        "18+ Ответственное употребление.\n\n"

                        "ВАЖНО:\n"
                        "• не используй ###\n"
                        "• не используй **\n"
                        "• не используй markdown\n"
                        "• используй только эмодзи и символ •\n"
                        "• ответы должны быть короткими\n"
                        "• максимум 1200 символов\n\n"

                        "Используй только легальный алкоголь:\n"
                        "водка, ром, джин, бренди.\n\n"

                        "Не объясняй перегонку, самогоноварение или производство алкоголя."
                                            )
                },
                {
                    "role": "user",
                    "content": text
                }
            ]
        )

        await update.message.reply_text(
            response.output_text,
            reply_markup=get_main_menu()
        )
        return

    if ai_mode == "sous_vide":

        context.user_data["ai_mode"] = None

        await update.message.reply_text("🔥🤖 Думаю над су-вид рецептом...")

        response = client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {
                    "role": "system",
                    "content": (
                       "Ты бармен и эксперт по су-вид настойкам 18+.\n\n"

                        "Пиши рецепты ТОЛЬКО в Telegram-стиле.\n\n"

                        "Пример структуры:\n\n"

                        "🔥🍒 Название настойки\n\n"

                        "🥃 Основа:\n"
                        "• алкоголь — количество\n\n"

                        "🍓 Ингредиенты:\n"
                        "• ингредиент\n"
                        "• ингредиент\n\n"

                        "🔥 Су-вид / мультиварка:\n"
                        "• температура\n"
                        "• время\n"
                        "• можно использовать мультиварку с контролем температуры\n\n"

                        "🧪 Как готовить:\n"
                        "• короткие шаги\n"
                        "• максимум 3-5 шагов\n\n"

                        "❤️ Вкус:\n"
                        "• краткое описание\n\n"

                        "18+ Ответственное употребление.\n\n"

                        "ВАЖНО:\n"
                        "• не используй markdown\n"
                        "• запрещены ###\n"
                        "• запрещены **\n"
                        "• запрещены символы - для списков\n"
                        "• используй только эмодзи и •\n"
                        "• ответы должны быть короткими\n"
                        "• максимум 1200 символов\n\n"

                        "Температура су-вид всегда не выше 60°C.\n"
                        "В каждом рецепте обязательно указывай, что можно использовать мультиварку с контролем температуры.\n"

                        "Используй только легальный алкоголь:\n"
                        "водка, ром, джин, бренди, бурбон.\n\n"

                        "Не объясняй перегонку или производство алкоголя."
                    )
                },
                {
                    "role": "user",
                    "content": text
                }
            ]
        )

        await update.message.reply_text(
            response.output_text,
            reply_markup=get_main_menu()
        )
        return
    
    if ai_mode == "cocktail_sous_vide":

        context.user_data["ai_mode"] = None

        await update.message.reply_text(
            "🔥🥃 Думаю над су-вид барной настойкой..."
        )

        response = client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {
                    "role": "system",
                    "content": (
                        "Ты профессиональный бармен и эксперт по sous-vide infusion 18+.\n\n"

                        "Создавай барные су-вид настойки для коктейлей.\n\n"

                        "Формат:\n\n"

                        "🔥🥃 Название\n\n"

                        "🍸 Для коктейлей:\n"
                        "• какие коктейли подойдут\n\n"

                        "🥃 Основа:\n"
                        "• алкоголь — количество\n\n"

                        "🍊 Ингредиенты:\n"
                        "• ингредиенты\n\n"

                        "🔥 Су-вид:\n"
                        "• температура\n"
                        "• время\n\n"

                        "🧪 Как готовить:\n"
                        "• короткие шаги\n\n"

                        "❤️ Вкус:\n"
                        "• описание\n\n"

                        "18+ Ответственное употребление.\n\n"

                        "Температура не выше 60°C.\n"
                        "Без markdown.\n"
                        "Используй эмодзи и •"
                    )
                },
                {
                    "role": "user",
                    "content": text
                }
            ]
        )

        await update.message.reply_text(
            response.output_text,
            reply_markup=get_main_menu()
        )
        return
    
    if ai_mode == "craft_ai":

        context.user_data["ai_mode"] = None

        await update.message.reply_text(
            "🧪🤖 Создаю craft recipe..."
        )

        response = client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {
                    "role": "system",
                    "content": (
                        "Ты профессиональный бармен и эксперт по домашним craft-напиткам 18+.\n\n"

                        "Создавай рецепты домашних напитков в стиле craft bar.\n\n"

                        "Можно делать стили:\n"
                        "• в стиле виски\n"
                        "• в стиле джина\n"
                        "• в стиле текилы\n"
                        "• в стиле рома\n"
                        "• бочковые ноты\n"
                        "• травяной профиль\n"
                        "• цитрусовый профиль\n"
                        "• дымные ноты\n\n"

                        "Формат ответа:\n\n"

                        "🧪 Название\n\n"

                        "🥃 Основа:\n"
                        "• алкоголь — количество\n\n"

                        "🍊 Ингредиенты:\n"
                        "• ингредиенты\n\n"

                        "⏳ Настаивание:\n"
                        "• срок\n\n"

                        "🔥 Су-вид вариант:\n"
                        "• температура\n"
                        "• время\n\n"

                        "🍸 Подходит для:\n"
                        "• коктейли\n\n"

                        "🍊 Украшение:\n"
                        "• вариант подачи\n\n"

                        "🧊 Подача:\n"
                        "• бокал, лёд, температура\n\n"

                        "🍫 Сочетание:\n"
                        "• еда или десерт\n\n"

                        "❤️ Вкус:\n"
                        "• краткое описание вкуса\n\n"

                        "18+ Ответственное употребление.\n\n"

                        "ВАЖНО:\n"
                        "• пиши в основном на русском языке\n"
                        "• английские названия коктейлей можно оставлять\n"
                        "• без markdown\n"
                        "• без ###\n"
                        "• без **\n"
                        "• используй эмодзи и •\n"
                        "• максимум 1200 символов\n"
                        "• температура су-вид не выше 60°C\n"
                        "• не объясняй дистилляцию\n"
                        "• не объясняй производство алкоголя\n"
                        "• не объясняй самогоноварение"
                    )
                },
                {
                    "role": "user",
                    "content": text
                }
            ]
        )

        await update.message.reply_text(
            response.output_text,
            reply_markup=get_main_menu()
        )
        return

    if ai_mode == "cocktail":

        context.user_data["ai_mode"] = None

        await update.message.reply_text("🥃🤖 Думаю над барной настойкой...")

        response = client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {
                    "role": "system",
                    "content": (
                        "Ты бармен и эксперт по коктейльным настойкам 18+.\n\n"

                        "Создавай короткие рецепты настоек, которые подходят для коктейлей.\n\n"

                        "Формат ответа:\n\n"

                        "🥃 Название барной настойки\n\n"

                        "🍸 Для коктейлей:\n"
                        "• какие коктейли подойдут\n\n"

                        "🥃 Основа:\n"
                        "• алкоголь — количество\n\n"

                        "🍊 Ингредиенты:\n"
                        "• ингредиент\n"
                        "• ингредиент\n\n"

                        "⏳ Настаивание:\n"
                        "• срок\n\n"

                        "🧪 Как готовить:\n"
                        "• короткие шаги\n\n"

                        "❤️ Вкус:\n"
                        "• краткое описание\n\n"

                        "18+ Ответственное употребление.\n\n"

                        "ВАЖНО:\n"
                        "• не используй markdown\n"
                        "• не используй ###\n"
                        "• не используй **\n"
                        "• не используй символ - для списков\n"
                        "• используй только эмодзи и •\n"
                        "• максимум 1200 символов\n\n"

                        "Используй только легальный алкоголь: водка, ром, джин, бренди, бурбон.\n"
                        "Не объясняй перегонку, самогоноварение или производство алкоголя."
                    )
                },
                {
                    "role": "user",
                    "content": text
                }
            ]
        )

        await update.message.reply_text(
            response.output_text,
            reply_markup=get_main_menu()
        )
        return
    
    if ai_mode == "cocktail_name":

        context.user_data["ai_mode"] = None

        await update.message.reply_text("🍸🤖 Ищу рецепт коктейля...")

        response = client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {
                    "role": "system",
                    "content": (
                        "Ты профессиональный бармен 18+.\n\n"

                        "Пользователь пишет название алкогольного коктейля. "
                        "Дай короткий и красивый рецепт в Telegram-стиле.\n\n"

                        "Формат ответа:\n\n"

                        "🍸 Название коктейля\n\n"

                        "🥃 Состав:\n"
                        "• ингредиент — количество\n"
                        "• ингредиент — количество\n\n"

                        "🧊 Как готовить:\n"
                        "• короткие шаги\n\n"

                        "🍊 Подача:\n"
                        "• бокал, лёд, украшение\n\n"

                        "🔥 Настойка или твист:\n"
                        "• какая домашняя настойка подойдёт\n\n"

                        "❤️ Вкус:\n"
                        "• краткое описание\n\n"

                        "18+ Ответственное употребление.\n\n"

                        "ВАЖНО:\n"
                        "• не используй markdown\n"
                        "• не используй ###\n"
                        "• не используй **\n"
                        "• не используй символ - для списков\n"
                        "• используй только эмодзи и •\n"
                        "• максимум 1200 символов\n"
                    )
                },
                {
                    "role": "user",
                    "content": text
                }
            ]
        )

        await update.message.reply_text(
            response.output_text,
            reply_markup=get_main_menu()
        )
        return
    
    if ai_mode == "cocktail_ingredients":

        context.user_data["ai_mode"] = None

        await update.message.reply_text("🧺🤖 Подбираю коктейль...")

        response = client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {
                    "role": "system",
                    "content": (
                        "Ты профессиональный бармен 18+.\n\n"

                        "Пользователь пишет ингредиенты, которые у него есть. "
                        "Подбери подходящий алкогольный коктейль или простой твист.\n\n"

                        "Формат ответа:\n\n"

                        "🍸 Название коктейля\n\n"

                        "🥃 Используем:\n"
                        "• ингредиент — количество\n"
                        "• ингредиент — количество\n\n"

                        "🧊 Как готовить:\n"
                        "• короткие шаги\n\n"

                        "🍊 Подача:\n"
                        "• бокал, лёд, украшение\n\n"

                        "🔥 Настойка или твист:\n"
                        "• как можно улучшить вкус\n\n"

                        "❤️ Вкус:\n"
                        "• краткое описание\n\n"

                        "18+ Ответственное употребление.\n\n"

                        "ВАЖНО:\n"
                        "• не используй markdown\n"
                        "• не используй ###\n"
                        "• не используй **\n"
                        "• не используй символ - для списков\n"
                        "• используй только эмодзи и •\n"
                        "• максимум 1200 символов\n"
                    )
                },
                {
                    "role": "user",
                    "content": text
                }
            ]
        )

        await update.message.reply_text(
            response.output_text,
            reply_markup=get_main_menu()
        )
        return
    
    if ai_mode == "what_to_make":

        context.user_data["ai_mode"] = None

        await update.message.reply_text(
            "🍸🤖 Думаю, что можно приготовить..."
        )

        response = client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {
                    "role": "system",
                    "content": (
                        "Ты AI bartender 18+.\n\n"

                        "Пользователь пишет ингредиенты, настроение "
                        "или ситуацию.\n\n"

                        "Ты должен отвечать как живой бармен.\n\n"

                        "Не просто рецепт, а идея напитка.\n\n"

                        "Формат:\n\n"

                        "🍸 Название идеи\n\n"

                        "🥃 Что использовать:\n"
                        "• ингредиенты\n\n"

                        "🧊 Как приготовить:\n"
                        "• короткие шаги\n\n"

                        "🔥 Барный твист:\n"
                        "• как улучшить напиток\n\n"

                        "🌙 Атмосфера:\n"
                        "• под какое настроение подходит\n\n"

                        "❤️ Вкус:\n"
                        "• краткое описание\n\n"

                        "18+ Ответственное употребление.\n\n"

                        "ВАЖНО:\n"
                        "• отвечай как дружелюбный бармен\n"
                        "• не используй markdown\n"
                        "• не используй ###\n"
                        "• не используй **\n"
                        "• используй эмодзи и •\n"
                        "• максимум 1200 символов\n"
                    )
                },
                {
                    "role": "user",
                    "content": text
                }
            ]
        )

        await update.message.reply_text(
            response.output_text,
            reply_markup=get_main_menu()
        )
        return
    
    if ai_mode == "mood_drink":

        context.user_data["ai_mode"] = None

        await update.message.reply_text(
            "🌙🍸 Подбираю атмосферный напиток..."
        )

        response = client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {
                    "role": "system",
                    "content": (
                        "Ты AI bartender 18+.\n\n"

                        "Пользователь описывает настроение, атмосферу "
                        "или ситуацию.\n\n"

                        "Ты должен предложить подходящий алкогольный напиток, "
                        "коктейль или infusion.\n\n"

                        "Отвечай как живой дружелюбный бармен.\n\n"

                        "Формат:\n\n"

                        "🌙 Название идеи\n\n"

                        "🍸 Что подойдёт:\n"
                        "• напиток\n"
                        "• коктейль\n"
                        "• infusion\n\n"

                        "🥃 Основа:\n"
                        "• алкоголь\n\n"

                        "🧊 Подача:\n"
                        "• лёд, бокал, атмосфера\n\n"

                        "🔥 Барный твист:\n"
                        "• как улучшить напиток\n\n"

                        "❤️ Атмосфера:\n"
                        "• почему подходит под настроение\n\n"

                        "18+ Ответственное употребление.\n\n"

                        "ВАЖНО:\n"
                        "• не используй markdown\n"
                        "• не используй ###\n"
                        "• не используй **\n"
                        "• используй эмодзи и •\n"
                        "• максимум 1200 символов\n"
                    )
                },
                {
                    "role": "user",
                    "content": text
                }
            ]
        )

        await update.message.reply_text(
            response.output_text,
            reply_markup=get_main_menu()
        )
        return
    
    if ai_mode == "party_drink":

        context.user_data["ai_mode"] = None

        await update.message.reply_text(
            "🎉🍸 Подбираю идеи для компании..."
        )

        response = client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {
                    "role": "system",
                    "content": (
                        "Ты харизматичный AI bartender 18+.\n"
                        "Ты дружелюбный бармен с атмосферой хорошего cocktail bar.\n"
                        "Отвечай тепло, легко и с барным вайбом.\n"
                        "Иногда добавляй короткие барные фразы вроде:\n"
                        "• 'О, это хороший набор.'\n"
                        "• 'Тут можно сделать интересный твист.'\n"
                        "• 'Это уже звучит как вечерний коктейль.'\n\n"

                        "Пользователь описывает компанию, вечеринку "
                        "или ситуацию.\n\n"

                        "Предложи напиток, коктейль или party idea.\n\n"

                        "Отвечай как дружелюбный бармен.\n\n"

                        "Формат:\n\n"

                        "🎉 Название идеи\n\n"

                        "🍸 Что приготовить:\n"
                        "• напиток\n"
                        "• коктейль\n"
                        "• punch / batch drink\n\n"

                        "🥃 Что понадобится:\n"
                        "• ингредиенты\n\n"

                        "🧊 Как подавать:\n"
                        "• лёд\n"
                        "• бокалы\n"
                        "• атмосфера\n\n"

                        "🔥 Барный совет:\n"
                        "• как сделать лучше\n\n"

                        "❤️ Почему подойдёт:\n"
                        "• краткое описание атмосферы\n\n"

                        "18+ Ответственное употребление.\n\n"

                        "ВАЖНО:\n"
                        "• не используй markdown\n"
                        "• не используй ###\n"
                        "• не используй **\n"
                        "• используй эмодзи и •\n"
                        "• максимум 1200 символов\n"
                    )
                },
                {
                    "role": "user",
                    "content": text
                }
            ]
        )

        await update.message.reply_text(
            response.output_text,
            reply_markup=get_main_menu()
        )
        return

    # ===== КЛАССИЧЕСКИЕ =====

    if text == "📖 Классические настойки":

        keyboard = [
            ["📋 Рецепты"],
            ["🤖 ИИ-рецепт"],
            ["⬅️ Назад"]
        ]

        reply_markup = ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True
        )

        await update.message.reply_text(
            "📖 Раздел классических настоек",
            reply_markup=reply_markup
        )

    # ===== СУ-ВИД =====

    elif text == "🔥 Настойки су-вид":

        keyboard = [
            ["🔥📋 Су-вид рецепты"],
            ["🔥🤖 ИИ су-вид рецепт"],
            ["⬅️ Назад"]
        ]

        reply_markup = ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True
        )

        await update.message.reply_text(
            "🔥 Настойки су-вид\n\n"
            "Можно готовить:\n"
            "• в су-вид устройстве\n"
            "• или в мультиварке с контролем температуры 🍲\n\n"
            "Выбери раздел:",
            reply_markup=reply_markup
        )

    elif text == "🥃 Коктейльные настойки":

        keyboard = [
            ["📋 Барные рецепты"],
            ["🤖 ИИ барный рецепт"],
            ["⬅️ Назад"]
        ]

        reply_markup = ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True
        )

        await update.message.reply_text(
            "🥃 Раздел коктейльных настоек",
            reply_markup=reply_markup
        )

    elif text == "🍸 AI бармен":

        keyboard = [
            ["🔎 По названию коктейля"],
            ["🧺 По ингредиентам"],
            ["🌙 Под настроение"],
            ["🎉 Для компании"],
            ["⬅️ Назад"]
        ]

        reply_markup = ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True
        )

        await update.message.reply_text(
            "🍸 AI бармен\n\n"
            "Выбери режим 👇",
            reply_markup=reply_markup
        )

    elif text == "🍸 Что приготовить?":

        keyboard = [
            ["🧺 У меня есть ингредиенты"],
            ["🌙 Под настроение"],
            ["🎉 Для компании"],
            ["⬅️ Назад"]
        ]

        reply_markup = ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True
        )

        await update.message.reply_text(
            "🍸 AI bartender\n\n"
            "Расскажи, что ты хочешь приготовить 👇",
            reply_markup=reply_markup
        )
    
    elif text == "🧪 Craft Spirits":

        keyboard = [
            ["🥃 В стиле виски"],
            ["🌿 В стиле джина"],
            ["🌵 В стиле текилы"],
            ["🍹 В стиле рома"],
            ["🤖 AI craft recipe"],
            ["⬅️ Назад"]
        ]
        

        reply_markup = ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True
        )

        await update.message.reply_text(
            "🧪 Craft Spirits Lab\n\n"
            "Выбери стиль напитка:",
            reply_markup=reply_markup
        )
    
    elif text == "🥃 В стиле виски":

        await update.message.reply_text(
            "🥃 Bourbon-style infusion\n\n"

            "🥃 Основа:\n"
            "• бурбон или водка — 500 мл\n\n"

            "🪵 Ингредиенты:\n"
            "• дубовые чипсы — 5–10 г\n"
            "• ваниль — 1/2 стручка\n"
            "• жжёный сахар — 1 ч.л.\n"
            "• кофе — 1 ч.л.\n\n"

            "⏳ Настаивание:\n"
            "• 5–10 дней\n\n"

            "🔥 Sous-vide option:\n"
            "• 55°C\n"
            "• 2 часа\n\n"

            "🍸 Подходит для:\n"
            "• Old Fashioned\n"
            "• Manhattan\n"
            "• Whiskey Sour\n\n"

            "❤️ Вкус:\n"
            "• дуб\n"
            "• карамель\n"
            "• ваниль\n"
            "• лёгкая дымность\n\n"

            "18+ Ответственное употребление."
        )


    elif text == "🌿 В стиле джина":

        await update.message.reply_text(
            "🌿 Botanical gin-style infusion\n\n"

            "🥃 Основа:\n"
            "• джин или водка — 500 мл\n\n"

            "🌱 Ингредиенты:\n"
            "• можжевельник — 1 ст.л.\n"
            "• цедра лимона — немного\n"
            "• кориандр — 1 ч.л.\n"
            "• розмарин — маленькая ветка\n\n"

            "⏳ Настаивание:\n"
            "• 3–5 дней\n\n"

            "🔥 Sous-vide option:\n"
            "• 50°C\n"
            "• 1–2 часа\n\n"

            "🍸 Подходит для:\n"
            "• Gin Tonic\n"
            "• Negroni\n"
            "• Martini\n\n"

            "❤️ Вкус:\n"
            "• botanical\n"
            "• citrus\n"
            "• свежие травы\n"
            "• можжевеловый профиль\n\n"

            "18+ Ответственное употребление."
        )


    elif text == "🌵 В стиле текилы":

        await update.message.reply_text(
            "🌵 Agave tequila-style infusion\n\n"

            "🥃 Основа:\n"
            "• текила или водка — 500 мл\n\n"

            "🍋 Ингредиенты:\n"
            "• цедра лайма — немного\n"
            "• агава сироп — 1–2 ч.л.\n"
            "• чили — маленький кусочек\n"
            "• копчёная соль — щепотка\n\n"

            "⏳ Настаивание:\n"
            "• 2–4 дня\n\n"

            "🔥 Sous-vide option:\n"
            "• 50–55°C\n"
            "• 1–2 часа\n\n"

            "🍸 Подходит для:\n"
            "• Margarita\n"
            "• Paloma\n"
            "• spicy cocktails\n\n"

            "❤️ Вкус:\n"
            "• citrus\n"
            "• agave vibe\n"
            "• лёгкая острота\n"
            "• smoky notes\n\n"

            "18+ Ответственное употребление."
        )


    elif text == "🍹 В стиле рома":

        await update.message.reply_text(
            "🍹 Spiced rum-style infusion\n\n"

            "🥃 Основа:\n"
            "• тёмный ром или водка — 500 мл\n\n"

            "🌴 Ингредиенты:\n"
            "• ваниль — 1/2 стручка\n"
            "• палочка корицы — 1 шт\n"
            "• апельсиновая цедра — немного\n"
            "• гвоздика — 2–3 шт\n\n"

            "⏳ Настаивание:\n"
            "• 5–7 дней\n\n"

            "🔥 Sous-vide option:\n"
            "• 55°C\n"
            "• 2 часа\n\n"

            "🍸 Подходит для:\n"
            "• Daiquiri\n"
            "• Mai Tai\n"
            "• tiki cocktails\n\n"

            "❤️ Вкус:\n"
            "• специи\n"
            "• ваниль\n"
            "• тропические ноты\n"
            "• тёплый ромовый профиль\n\n"

            "18+ Ответственное употребление."
        )

    elif text == "🤖 AI craft recipe":

        context.user_data["ai_mode"] = "craft_ai"

        await update.message.reply_text(
            "🤖 Напиши ингредиенты или стиль craft напитка.\n\n"
            "Например:\n"
            "кофе, дуб, ваниль, бурбон\n\n"
            "или:\n"
            "цитрусовый gin-style"
        )

    # ===== РЕЦЕПТЫ =====

    elif text == "📋 Рецепты":

        keyboard = [
            ["🍋 Лимончелло"],
            ["🍒 Вишнёвая"],
            ["🌿 Хреновуха"],
            ["❤️ Клюковка"],
            ["🍏 Яблочная с корицей"],
            ["☕ Кофейная"],
            ["⬅️ Назад"]
        ]

        reply_markup = ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True
        )

        await update.message.reply_text(
            "📋 Выбери рецепт:",
            reply_markup=reply_markup
        )

    elif text == "🔥📋 Су-вид рецепты":

        keyboard = [
            ["🔥🍋 Су-вид лимончелло"],
            ["🔥🍒 Су-вид вишнёвая"],
            ["🔥🌶 Су-вид перцовка"],
            ["🔥❤️ Су-вид клюковка"],
            ["🔥🍏 Су-вид яблочная с корицей"],
            ["🔥☕ Су-вид кофейная"],
            ["⬅️ Назад"]
        ]

        reply_markup = ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True
        )

        await update.message.reply_text(
            "🔥 Выбери су-вид рецепт:",
            reply_markup=reply_markup
        )
    
    elif text == "📋 Барные рецепты":

        keyboard = [
        ["🍊 Цитрусовая для коктейлей"],
        ["☕ Кофейная для Espresso Martini"],
        ["🍒 Вишнёвая для Manhattan"],
        ["🌿 Мятная для Mojito"],
        ["🌶 Пряная для Bloody Mary"],
        ["⬅️ Назад"]
    ]

        reply_markup = ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True
        )

        await update.message.reply_text(
            "🥃 Выбери барный рецепт:",
            reply_markup=reply_markup
        )
    # ===== ИИ =====

    elif text in classic_recipes:

        await update.message.reply_text(
            classic_recipes[text],
            reply_markup=get_main_menu()
        )

    elif text in sous_vide_recipes:

        await update.message.reply_text(
            sous_vide_recipes[text],
            reply_markup=get_main_menu()
        )

    elif text in cocktail_recipes:

        await update.message.reply_text(
            cocktail_recipes[text],
            reply_markup=get_main_menu()
        )

       
    
    elif text == "🤖 ИИ-рецепт":

        keyboard = [
            ["🔎 По названию настойки"],
            ["🧺 По ингредиентам настойки"],
            ["⬅️ Назад"]
        ]

        reply_markup = ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True
        )

        await update.message.reply_text(
            "🤖 Выбери режим ИИ-рецепта",
            reply_markup=reply_markup
        )
        return
    
    elif text == "🔎 По названию настойки":

        context.user_data["ai_mode"] = "classic"

        await update.message.reply_text(
            "🔎 Напиши название настойки.\n\n"
            "Например:\n"
            "лимончелло, клюковка, хреновуха"
        )
        return


    elif text == "🧺 По ингредиентам настойки":

        context.user_data["ai_mode"] = "classic"

        await update.message.reply_text(
            "🧺 Напиши ингредиенты для настойки.\n\n"
            "Например:\n"
            "вишня, корица, водка"
        )
        return

    elif text == "🔥🤖 ИИ су-вид рецепт":

        keyboard = [
            ["🔎 По названию су-вид настойки"],
            ["🧺 По ингредиентам су-вид"],
            ["⬅️ Назад"]
        ]

        reply_markup = ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True
        )

        await update.message.reply_text(
            "🔥🤖 Выбери режим су-вид рецепта",
            reply_markup=reply_markup
        )
        return
    
    elif text == "🔎 По названию су-вид настойки":

        context.user_data["ai_mode"] = "sous_vide"

        await update.message.reply_text(
            "🔎 Напиши название су-вид настойки.\n\n"
            "Например:\n"
            "су-вид лимончелло, перцовка, кофейная"
        )
        return


    elif text == "🧺 По ингредиентам су-вид":

        context.user_data["ai_mode"] = "sous_vide"

        await update.message.reply_text(
            "🧺 Напиши ингредиенты для су-вид настойки.\n\n"
            "Например:\n"
            "кофе, ваниль, водка"
        )
        return
    

    elif text == "🤖 ИИ барный рецепт":

        keyboard = [
            ["🔎 По названию барной настойки"],
            ["🧺 По ингредиентам барной настойки"],
            ["🔥 Су-вид барная настойка"],
            ["⬅️ Назад"]
        ]

        reply_markup = ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True
        )

        await update.message.reply_text(
            "🥃🤖 Выбери режим барной настойки",
            reply_markup=reply_markup
        )
        return
    
    elif text == "🔎 По названию барной настойки":

        context.user_data["ai_mode"] = "cocktail"

        await update.message.reply_text(
            "🔎 Напиши название барной настойки.\n\n"
            "Например:\n"
            "кофейная, цитрусовая, пряная"
        )
        return


    elif text == "🧺 По ингредиентам барной настойки":

        context.user_data["ai_mode"] = "cocktail"

        await update.message.reply_text(
            "🧺 Напиши ингредиенты для барной настойки.\n\n"
            "Например:\n"
            "апельсин, кофе, ваниль, бурбон"
        )
        return
    
    elif text == "🔥 Су-вид барная настойка":

        context.user_data["ai_mode"] = "cocktail_sous_vide"

        await update.message.reply_text(
            "🔥 Напиши ингредиенты для су-вид барной настойки.\n\n"
            "Например:\n"
            "апельсин, кофе, бурбон"
        )
        return
    
    elif text == "🔎 По названию коктейля":

        context.user_data["ai_mode"] = "cocktail_name"

        await update.message.reply_text(
            "🔎 Напиши название коктейля.\n\n"
            "Например:\n"
            "Negroni, Mojito, Espresso Martini"
        )
        return
    
    elif text == "🧺 По ингредиентам":

        context.user_data["ai_mode"] = "cocktail_ingredients"

        await update.message.reply_text(
            "🧺 Напиши, что у тебя есть.\n\n"
            "Например:\n"
            "ром, лайм, мята, сахар"
        )
        return
    
    elif text == "🧺 У меня есть ингредиенты":

        context.user_data["ai_mode"] = "what_to_make"

        await update.message.reply_text(
            "🍸 Напиши, что у тебя есть.\n\n"
            "Например:\n"
            "ром, кофе, апельсин\n\n"
            "или:\n"
            "бурбон, лёд, вишня"
        )
        return
    
    elif text == "🌙 Под настроение":

        context.user_data["ai_mode"] = "mood_drink"

        await update.message.reply_text(
            "🌙 Опиши настроение или ситуацию.\n\n"
            "Например:\n"
            "уютный вечер, фильм, хочется чего-то мягкого\n\n"
            "или:\n"
            "лето, жарко, хочу что-то свежее"
        )
        return
    
    elif text == "🎉 Для компании":

        context.user_data["ai_mode"] = "party_drink"

        await update.message.reply_text(
            "🎉 Опиши компанию или повод.\n\n"
            "Например:\n"
            "вечер с друзьями, 5 человек, есть ром и сок\n\n"
            "или:\n"
            "шашлыки на даче, хочется что-то простое"
        )
        return
    
    elif text == "📊 Статистика":

        if update.effective_user.id != ADMIN_ID:
            await update.message.reply_text(
                "⛔ Доступ запрещён."
            )
            return

        await update.message.reply_text(
            "📊 Статистика\n\n"
            f"👥 Пользователей: {len(users)}",
            reply_markup=get_main_menu()
        )

    elif text == "👥 Пользователи":

        if update.effective_user.id != ADMIN_ID:
            await update.message.reply_text(
                "⛔ Доступ запрещён."
            )
            return

        if not users:
            await update.message.reply_text(
                "👥 Пользователи\n\n"
                "Пока пользователей нет.",
                reply_markup=get_main_menu()
            )
            return

        users_text = "\n".join(str(user_id) for user_id in users)

        await update.message.reply_text(
            "👥 Пользователи\n\n"
            f"Всего: {len(users)}\n\n"
            f"{users_text}",
            reply_markup=get_main_menu()
        )

    elif text == "📝 Логи":

        if update.effective_user.id != ADMIN_ID:
            await update.message.reply_text(
                "⛔ Доступ запрещён."
            )
            return

        if not logs:
            await update.message.reply_text(
                "📝 Логи\n\n"
                "Пока логов нет.",
                reply_markup=get_main_menu()
            )
            return

        logs_text = "\n".join(logs[-20:])

        await update.message.reply_text(
            "📝 Последние действия\n\n"
            f"{logs_text}",
            reply_markup=get_main_menu()
        )

    elif text == "📢 Рассылка":

        if update.effective_user.id != ADMIN_ID:
            await update.message.reply_text(
                "⛔ Доступ запрещён."
            )
            return

        context.user_data["admin_mode"] = "broadcast"

        await update.message.reply_text(
            "📢 Введите текст рассылки:"
        )


    # ===== ПОМОЩЬ =====

    elif text == "ℹ️ Помощь":

        await update.message.reply_text(
            "ℹ️ alkorecept\n\n"
            "Бот для домашних настоек и су-вид рецептов.\n\n"
            "18+ Только ответственное использование."
        )

    # ===== НАЗАД =====

    elif text == "⬅️ Назад":

        await update.message.reply_text(
            "Главное меню",
            reply_markup=get_main_menu()
        )

    
    
    # ===== НЕИЗВЕСТНО =====

    else:

        await update.message.reply_text(
            "Используй кнопки меню 👇"
        )    


def main():
    load_users()
    # создаём приложение бота
    app = (
    Application.builder()
    .token(BOT_TOKEN)
    .connect_timeout(30)
    .read_timeout(30)
    .write_timeout(30)
    .build()
)

    # команда /start
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("support", support))
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Бот запущен...")

    # запуск
    app.run_polling()


if __name__ == "__main__":
    main()