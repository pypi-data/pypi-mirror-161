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

import tegram

from ..object import Object

"""- :obj:`~tegram.types.InputLocationMessageContent`
    - :obj:`~tegram.types.InputVenueMessageContent`
    - :obj:`~tegram.types.InputContactMessageContent`"""


class InputMessageContent(Object):
    """Content of a message to be sent as a result of an inline query.

    tegram currently supports the following types:

    - :obj:`~tegram.types.InputTextMessageContent`
    """

    def __init__(self):
        super().__init__()

    async def write(self, client: "tegram.Client", reply_markup):
        raise NotImplementedError
