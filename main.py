import asyncio
import logging
import os
import sys
from datetime import datetime, timedelta, timezone

from aiogram import Bot, Dispatcher
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import (InlineQuery, InlineQueryResultArticle,
                           InputTextMessageContent, Message)
from dotenv import find_dotenv, load_dotenv

from stk_parser import get_detections, get_stk_token

load_dotenv(find_dotenv(), verbose=True)
BOT_TOKEN :str = os.environ.get('BOT_TOKEN', 'ERR')

dp = Dispatcher()
bot = Bot(BOT_TOKEN)



async def main() -> None:

    await dp.start_polling(bot)


@dp.message(CommandStart())
async def start_handler(message: Message) -> None:
    print('Alive!')


@dp.message(Command(
        'on',
        prefix='\\/!.'))
async def on_handler(message: Message, command: CommandObject) -> None:
    '''contious checking detections and inform in telegram

    :param Message message: returned message
    :param CommandObject command: returned command with args
    '''
    token = await get_stk_token()
    new_msg_ = True
    exterminate_timer = 1200 # in seconds
    t = command.args
    if t:
        match t[-1]:
            case 's': # 30s
                timeout = int(t[:-1])
                timeout_hint = f'{t[:-1]} seconds'
            case 'm': # 10m
                timeout = int(t[:-1]) * 60
                timeout_hint = f'{t[:-1]} minutes'
            case 'h': # 1h
                timeout = int(t[:-1]) * 60 * 60
                timeout_hint = f'{t[:-1]} hour'
            case _: # 137
                timeout = int(t)
                timeout_hint = f'{t} seconds'
    else:
        timeout = 58
        timeout_hint = '1 minute'
    await bot.send_message(message.chat.id, f'update every {timeout_hint}\n', disable_notification=True,)

    while True:
        try:
            status, d, d_count = await get_detections(token)
            if status != 200:
                # bad request
                token = await get_stk_token()
                print(f'taken new stk token: ..{token[-8:]}')
                continue

            d_count = 'zero' if not d_count else d_count
            d_now = f'`{datetime.now(tz=timezone(timedelta(hours=5))).strftime("%H:%M:%S")}` \- {d_count} detections' # type: ignore
            if new_msg_:
                sended = await bot.send_message(message.chat.id, d_now, disable_notification=True, parse_mode='MarkdownV2')
                new_msg_ = False
            else:
                if (int(datetime.timestamp(datetime.now(tz=timezone(timedelta(hours=5))))) - int(datetime.timestamp(sended.date))) >= exterminate_timer:
                    # delete old messages and send new
                    await bot.delete_message(sended.chat.id, sended.message_id)
                    sended = await bot.send_message(message.chat.id, d_now, disable_notification=True, parse_mode='MarkdownV2')

                else:
                    if sended:
                        await bot.edit_message_text(d_now, sended.chat.id, sended.message_id, parse_mode='MarkdownV2')
        except Exception as e:
            print(e)
            continue
        await asyncio.sleep(timeout) # in seconds



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
    print(f'wrong token:{BOT_TOKEN} 'if BOT_TOKEN == 'ERR' else f'started at {datetime.now(tz=timezone(timedelta(hours=5))).strftime("%H:%M:%S")}')
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
