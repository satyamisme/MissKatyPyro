import asyncio

from pyrogram import filters
from pyrogram.errors import MessageDeleteForbidden

data = {}


async def task(msg, warn=False, sec=None):
    if warn:
        user = msg.from_user
        ids = await msg.reply_msg(
            f"Sorry {user.mention} [<code>{user.id}</code>], you must wait for {sec}s before using feature again.."
        )
        try:
            await msg.delete_msg()
        except MessageDeleteForbidden:
            pass
        await asyncio.sleep(sec)
        await ids.edit_msg(
            f"Alright {user.mention} [<code>{user.id}</code>], your cooldown is over you can command again.",
            del_in=3,
        )


def wait(sec):
    async def ___(flt, _, msg):
        user_id = msg.from_user.id
        if user_id in data:
            if msg.date.timestamp() >= data[user_id]["timestamp"] + flt.data:
                data[user_id] = {"timestamp": msg.date.timestamp(), "warned": False}
                return True
            else:
                if not data[user_id]["warned"]:
                    data[user_id]["warned"] = True
                    asyncio.ensure_future(
                        task(msg, True, flt.data)
                    )  # for super accuracy use (future - time.time())
                    return False  # cause we dont need delete again

                asyncio.ensure_future(task(msg))
                return False
        else:
            data.update({user_id: {"timestamp": msg.date.timestamp(), "warned": False}})
            return True

    return filters.create(___, data=sec)
