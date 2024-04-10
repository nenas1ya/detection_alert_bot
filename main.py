import asyncio, logging, sys, os
from datetime import  datetime

from os.path import join, dirname
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.types import Message, InlineQuery, InlineQueryResultArticle,InputTextMessageContent


from stk_parser import get_detections, get_stk_token

#TODO remake funtional to OOP
#     try catch
#     change prints to tg_bot module


load_dotenv(join(dirname(__file__),'.env'))
BOT_TOKEN :str = os.environ.get('BOT_TOKEN', '')

dp = Dispatcher()
bot = Bot(BOT_TOKEN)


async def main() -> None:
    await dp.start_polling(bot)


@dp.message(CommandStart())
async def start_handler(message: Message) -> None:
    print('Alive!')

@dp.message(Command(
        'on',
        prefix='/!.'))
async def on_handler(message: Message, command: CommandObject) -> None:
    '''continious checking'''
    token = await get_stk_token()
    new_msg_ = True
    exterminate_timer = 3 # in minute
    t = command.args
    if t:
        match t[-1]:
            case 's': # 30s
                timeout = int(t[:-1])
                timeout_hint = f'{t[:-1]} seconds'
            case 'm': # 10m
                timeout = int(t[:-1]) * 60 
                timeout_hint = f'{t} minutes'
            case 'h': # 1h
                timeout = int(t[:-1]) * 60 * 60
                timeout_hint = f'{t[:-1]} hour'
            case _: # 137
                timeout = int(t)
                timeout_hint = f'{t[:-1]} seconds'
    else: 
        timeout = 60
        timeout_hint = '1 minute'
    await bot.send_message(message.chat.id, f'start polling every {timeout_hint}')

    while True:
        status, d = await get_detections(token)
        if status != 200:
            # bad request
            token = await get_stk_token()

            print(f'taken new stk token: ..{token[:-10]}')
            continue

        match len(d):
            case 0: d_count = 'zero'
            case _: d_count = len(d)

        d_now = f'{datetime.now().strftime("%H:%M:%S")} - {d_count} detections'
        if new_msg_:
            sended = await bot.send_message(message.chat.id, d_now)
            new_msg_ = False
        else:
            if (datetime.now().minute - sended.date.minute) >= exterminate_timer:
                # delete old messages and send new
                await bot.delete_message(sended.chat.id, sended.message_id)
                sended = await bot.send_message(message.chat.id, d_now)
                
            else:
                if sended:
                    await bot.edit_message_text(d_now, sended.chat.id, sended.message_id)

        await asyncio.sleep(timeout) # in seconds


@dp.message(Command(
        'now',
        prefix='/!.'))
async def now_handler(message: Message, command: CommandObject):
    '''one time statistic'''
    token = await get_stk_token()
    status, d_awaiting, await_count = await get_detections(token)
    status, d_valid, valid_count = await get_detections(
        token,
        status='VALID_DETECTION',
        created_gte=str(datetime.now())[:10]
    )
    status, d_invalid, invalid_count = await get_detections(
        token,
        status='INVALID_DETECTION',
        created_gte=str(datetime.now())[:10]
    )
    print(str(datetime.now())[:10])
    d_clicked = valid_count + invalid_count 
    text = f'{await_count} awaiting now | {valid_count+invalid_count} clicked today'
    await bot.send_message(message.chat.id, text)


@dp.inline_query()
async def inline_handler(inline_query: InlineQuery):
    token = await get_stk_token()
    status, d_awaiting, await_count = await get_detections(token)
    result = [
        InlineQueryResultArticle(
            id=str(datetime.now().timestamp()+10),
            title='awaiting detections',
            input_message_content=InputTextMessageContent(
                message_text=f'{await_count} awaiting detections'
            ),
        )
    ]
    await inline_query.answer(result, is_personal=True, cache_time=30) # type: ignore

if __name__ == "__main__":
    print(str(datetime.now())[:10])
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())


