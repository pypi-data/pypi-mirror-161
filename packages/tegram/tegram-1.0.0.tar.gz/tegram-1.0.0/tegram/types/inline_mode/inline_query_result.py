#  tegram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
#
#  This file is part of tegram.
#
#  tegram is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  tegram is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with tegram.  If not, see <http://www.gnu.org/licenses/>.

from uuid import uuid4

import tegram
from tegram import types
from ..object import Object


class InlineQueryResult(Object):
    """One result of an inline query.

    - :obj:`~tegram.types.InlineQueryResultCachedAudio`
    - :obj:`~tegram.types.InlineQueryResultCachedDocument`
    - :obj:`~tegram.types.InlineQueryResultCachedAnimation`
    - :obj:`~tegram.types.InlineQueryResultCachedPhoto`
    - :obj:`~tegram.types.InlineQueryResultCachedSticker`
    - :obj:`~tegram.types.InlineQueryResultCachedVideo`
    - :obj:`~tegram.types.InlineQueryResultCachedVoice`
    - :obj:`~tegram.types.InlineQueryResultArticle`
    - :obj:`~tegram.types.InlineQueryResultAudio`
    - :obj:`~tegram.types.InlineQueryResultContact`
    - :obj:`~tegram.types.InlineQueryResultDocument`
    - :obj:`~tegram.types.InlineQueryResultAnimation`
    - :obj:`~tegram.types.InlineQueryResultLocation`
    - :obj:`~tegram.types.InlineQueryResultPhoto`
    - :obj:`~tegram.types.InlineQueryResultVenue`
    - :obj:`~tegram.types.InlineQueryResultVideo`
    - :obj:`~tegram.types.InlineQueryResultVoice`
    """

    def __init__(
        self,
        type: str,
        id: str,
        input_message_content: "types.InputMessageContent",
        reply_markup: "types.InlineKeyboardMarkup"
    ):
        super().__init__()

        self.type = type
        self.id = str(uuid4()) if id is None else str(id)
        self.input_message_content = input_message_content
        self.reply_markup = reply_markup

    async def write(self, client: "tegram.Client"):
        pass
