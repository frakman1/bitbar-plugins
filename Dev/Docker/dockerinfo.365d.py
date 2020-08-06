#!/usr/bin/python
# -*- encoding: utf-8 -*-

import os, sys
import argparse
import subprocess
import simplejson, urllib
import json
import re
from time import sleep
import pexpect
import logging
#import yaml

ME_PATH = os.path.realpath(__file__)

dockerinfodata_path = os.path.dirname(os.path.abspath(__file__)) +'/'+"dockerinfo_data"
if not os.path.exists(dockerinfodata_path) :
    os.mkdir( dockerinfodata_path, 0755 );
local_path = dockerinfodata_path+'/'+"local.txt"
remote_path = dockerinfodata_path+'/'+"remote.txt"
ip_path = dockerinfodata_path+'/'+"ip.txt"
user_path = dockerinfodata_path+'/'+"user.txt"
passwd_path = dockerinfodata_path+'/'+"passwd.txt"


os.environ["PATH"] += os.pathsep + '/usr/local/bin'
DOCKER_PATH = 'docker'
DOCKERPS_CMD = DOCKER_PATH + " ps -a --format '{{.ID}}^^{{.Image}}^^{{.Command}}^^{{.Status}}^^{{.Names}}'"
DOCKERIMAGES_CMD = DOCKER_PATH + ' images --format "{{.Repository}}^^{{.Tag}}^^{{.ID}}^^{{.CreatedSince}}^^{{.Size}}"'
REMOTE_DAEMON_PATH = '/etc/docker/daemon.json'
LOCAL_DAEMON_PATH = os.path.join(os.path.expanduser("~"),'.docker/daemon.json')
LOCAL_PROMPT = '.*[#\$]'
log_icon = 'iVBORw0KGgoAAAANSUhEUgAAABYAAAAWCAYAAADEtGw7AAAMJmlDQ1BJQ0MgUHJvZmlsZQAASImVlwdYU8kWgOeWVBJaIAJSQm+CCNKl1wAC0sFGSAIJJYaEoGJHFhVYCyoiWNFVERXXAshiw14Wwd4fFlSUdbFgQ+VNEkBXv/fe906+uffPmTNnzjmZO7kDgFo0RyzORtUByBHlSWJC/FlJySks0mOAwA8VaAEyhysV+0VHRwAoQ/d/yrvr0BbKFTu5r5/7/6to8PhSLgBINOQ0npSbA/kAALgLVyzJA4DQA/Wm0/PEkIkwSqAlgQFCNpNzhpLd5Jym5AiFTVxMAORUAMg0DkeSAYCqPC5WPjcD+lEtg+wg4glFkFsge3MFHB7kz5BH5eRMg6xmBdkq7Ts/Gf/wmTbsk8PJGGZlLgohBwql4mzOzP+zHP9bcrJlQ3OYwkYTSEJj5DnL65Y1LVzONMhnRWmRUZA1IV8V8hT2cn4ikIXGD9p/4EoDYM0AEwCUxuMEhkPWh2wiyo6MGNR7pwuD2ZBh7dE4YR47TjkW5UmmxQz6R2fwpUGxQ8yRKOaS25TIsuL9Bn1uEPDZQz6bCwRxico40fZ8YUIkZFXId6VZseGDNs8LBAGRQzYSWYw8ZvibYyBdEhyjtMHMcqRDeWEeAiE7cpAj8gRxocqx2BQuRxGbDuRMvjQpYihOHj8wSJkXVsgXxQ/Gj5WL8/xjBu23irOjB+2xFn52iFxvArlNmh87NLY3Dy42Zb44EOdFxyljw7UyOWHRyhhwGxABAkAgYAEZbGlgGsgEwraexh74TdkTDDhAAjIAH9gNaoZGJCp6RPAaCwrAX5D4QDo8zl/Rywf5UP9lWKu82oF0RW++YkQWeAI5B4SDbPhdphglGp4tATyGGuFPs3NhrNmwyft+0rHUhnTEIGIgMZQYTLTG9XBv3BOPgFdf2BxxN9x9KK5v9oQnhA7CQ8I1Qifh1lRhoeSHyFlgPOiEMQYPZpf2fXa4BfTqjPvjXtA/9I0zcT1gh4+FM/nhPnBuZ6j9PlbZcMbfajnoi+JAQSkjKL4Uqx8jULVRdR72Iq/U97VQxpU2XK2A4Z4f8wj4rn48eA//0RJbjO3HzmDHsXNYC9YIWNhRrAm7iB2W8/DaeKxYG0OzxSjiyYJ+hD/NxxmcU141qUOdQ7fD58E+kMefkSd/WAKmiWdKhBmCPJYf3K35LLaIaz+K5ejg6ACAfO9Xbi1vmIo9HWGe/6bLPQaAewlUZnzTceAedOgJAIx333Smr+GyXw7A4XauTJKv1OHyCwH+o6jBJ0UXGMK9ywpm5AhcgCfwBUEgDESBOJAMpsA6C+A6lYDpYDZYAIpBKVgOVoMqsBFsATvAbrAPNIIWcBycBhdAO7gG7sC10gVegF7wDvQjCEJC6AgD0UWMEHPEFnFE3BBvJAiJQGKQZCQVyUBEiAyZjSxESpFypArZjNQivyOHkOPIOaQDuYU8QLqR18gnFENpqBZqgFqgo1E31A8NR+PQyWgGmosWoEXoUrQSrUF3oQ3ocfQCeg3tRF+gfRjAVDAmZozZYW5YABaFpWDpmASbi5VgFVgNtgdrhr/0FawT68E+4kScgbNwO7heQ/F4nIvn4nPxMrwK34E34CfxK/gDvBf/SqAT9Am2BA8Cm5BEyCBMJxQTKgjbCAcJp+Cz00V4RyQSmURLoit89pKJmcRZxDLiemI98Rixg/iI2EcikXRJtiQvUhSJQ8ojFZPWknaRjpIuk7pIH8gqZCOyIzmYnEIWkQvJFeSd5CPky+Sn5H6KOsWc4kGJovAoMynLKFspzZRLlC5KP1WDakn1osZRM6kLqJXUPdRT1LvUNyoqKiYq7ioTVIQq81UqVfaqnFV5oPKRpkmzoQXQJtFktKW07bRjtFu0N3Q63YLuS0+h59GX0mvpJ+j36R9UGar2qmxVnuo81WrVBtXLqi/VKGrman5qU9QK1CrU9qtdUutRp6hbqAeoc9TnqlerH1K/od6nwdAYoxGlkaNRprFT45zGM02SpoVmkCZPs0hzi+YJzUcMjGHKCGBwGQsZWxmnGF1aRC1LLbZWplap1m6tNq1ebU3tsdoJ2jO0q7UPa3cyMaYFk83MZi5j7mNeZ34aYTDCbwR/xJIRe0ZcHvFeZ6SOrw5fp0SnXueaziddlm6QbpbuCt1G3Xt6uJ6N3gS96Xob9E7p9YzUGuk5kjuyZOS+kbf1UX0b/Rj9Wfpb9C/q9xkYGoQYiA3WGpww6DFkGvoaZhquMjxi2G3EMPI2EhqtMjpq9JylzfJjZbMqWSdZvcb6xqHGMuPNxm3G/SaWJvEmhSb1JvdMqaZupummq0xbTXvNjMzGm802qzO7bU4xdzMXmK8xP2P+3sLSItFikUWjxTNLHUu2ZYFlneVdK7qVj1WuVY3VVWuitZt1lvV663Yb1MbZRmBTbXPJFrV1sRXarrftGEUY5T5KNKpm1A07mp2fXb5dnd0De6Z9hH2hfaP9y9Fmo1NGrxh9ZvRXB2eHbIetDnfGaI4JG1M4pnnMa0cbR65jteNVJ7pTsNM8pyanV2Ntx/LHbhh705nhPN55kXOr8xcXVxeJyx6Xblcz11TXda433LTcot3K3M66E9z93ee5t7h/9HDxyPPY5/G3p51nludOz2fjLMfxx20d98jLxIvjtdmr05vlneq9ybvTx9iH41Pj89DX1Jfnu833qZ+1X6bfLr+X/g7+Ev+D/u8DPALmBBwLxAJDAksC24I0g+KDqoLuB5sEZwTXBfeGOIfMCjkWSggND10ReoNtwOaya9m9Ya5hc8JOhtPCY8Orwh9G2ERIIprHo+PDxq8cfzfSPFIU2RgFothRK6PuRVtG50b/MYE4IXpC9YQnMWNiZseciWXETo3dGfsuzj9uWdydeKt4WXxrglrCpITahPeJgYnliZ1Jo5PmJF1I1ksWJjelkFISUral9E0Mmrh6Ytck50nFk65Ptpw8Y/K5KXpTsqccnqo2lTN1fyohNTF1Z+pnThSnhtOXxk5bl9bLDeCu4b7g+fJW8br5Xvxy/tN0r/Ty9GcZXhkrM7oFPoIKQY8wQFglfJUZmrkx831WVNb2rIHsxOz6HHJOas4hkaYoS3RymuG0GdM6xLbiYnFnrkfu6txeSbhkmxSRTpY25WnBl+yLMivZL7IH+d751fkfpidM3z9DY4ZoxsWZNjOXzHxaEFzw2yx8FndW62zj2QtmP5jjN2fzXGRu2tzWeabziuZ1zQ+Zv2MBdUHWgj8LHQrLC98uTFzYXGRQNL/o0S8hv9QVqxZLim8s8ly0cTG+WLi4bYnTkrVLvpbwSs6XOpRWlH4u45ad/3XMr5W/DixNX9q2zGXZhuXE5aLl11f4rNhRrlFeUP5o5fiVDatYq0pWvV09dfW5irEVG9dQ18jWdFZGVDatNVu7fO3nKkHVtWr/6vp1+uuWrHu/nrf+8gbfDXs2Gmws3fhpk3DTzc0hmxtqLGoqthC35G95sjVh65nf3H6r3aa3rXTbl+2i7Z07YnacrHWtrd2pv3NZHVonq+veNWlX++7A3U177PZsrmfWl+4Fe2V7n/+e+vv1feH7Wve77d9zwPzAuoOMgyUNSMPMht5GQWNnU3JTx6GwQ63Nns0H/7D/Y3uLcUv1Ye3Dy45QjxQdGThacLTvmPhYz/GM449ap7beOZF04urJCSfbToWfOns6+PSJM35njp71OttyzuPcofNu5xsvuFxouOh88eCfzn8ebHNpa7jkeqmp3b29uWNcx5HLPpePXwm8cvoq++qFa5HXOq7HX795Y9KNzpu8m89uZd96dTv/dv+d+XcJd0vuqd+ruK9/v+Zf1v+q73TpPPwg8MHFh7EP7zziPnrxWPr4c1fRE/qTiqdGT2ufOT5r6Q7ubn8+8XnXC/GL/p7ivzT+WvfS6uWBv33/vtib1Nv1SvJq4HXZG90329+OfdvaF913/13Ou/73JR90P+z46PbxzKfET0/7p38mfa78Yv2l+Wv417sDOQMDYo6Eo3gVwGBD09MBeL0dAHoyfHdoB4A6UXk2UwiiPE8qCPwnVp7fFOICwHZfAOLnAxAB31E2wGYOmQbv8lfwOF+AOjkNt0GRpjs5Kn3R4ImF8GFg4I0BAKRmAL5IBgb61w8MfNkKg70FwLFc5ZlQLvIz6CZ7ObV3vQQ/yr8BUVRxAwLXS5UAAAAJcEhZcwAACxMAAAsTAQCanBgAAAILaVRYdFhNTDpjb20uYWRvYmUueG1wAAAAAAA8eDp4bXBtZXRhIHhtbG5zOng9ImFkb2JlOm5zOm1ldGEvIiB4OnhtcHRrPSJYTVAgQ29yZSA1LjQuMCI+CiAgIDxyZGY6UkRGIHhtbG5zOnJkZj0iaHR0cDovL3d3dy53My5vcmcvMTk5OS8wMi8yMi1yZGYtc3ludGF4LW5zIyI+CiAgICAgIDxyZGY6RGVzY3JpcHRpb24gcmRmOmFib3V0PSIiCiAgICAgICAgICAgIHhtbG5zOnRpZmY9Imh0dHA6Ly9ucy5hZG9iZS5jb20vdGlmZi8xLjAvIj4KICAgICAgICAgPHRpZmY6UmVzb2x1dGlvblVuaXQ+MjwvdGlmZjpSZXNvbHV0aW9uVW5pdD4KICAgICAgICAgPHRpZmY6Q29tcHJlc3Npb24+MTwvdGlmZjpDb21wcmVzc2lvbj4KICAgICAgICAgPHRpZmY6T3JpZW50YXRpb24+MTwvdGlmZjpPcmllbnRhdGlvbj4KICAgICAgICAgPHRpZmY6UGhvdG9tZXRyaWNJbnRlcnByZXRhdGlvbj4yPC90aWZmOlBob3RvbWV0cmljSW50ZXJwcmV0YXRpb24+CiAgICAgIDwvcmRmOkRlc2NyaXB0aW9uPgogICA8L3JkZjpSREY+CjwveDp4bXBtZXRhPgoPRSqTAAAEZklEQVQ4EY1VS2hcVRj+zjn3Ma80E5OpqWmjLY2U1pWCoKidLgIKWfggpV04kIU2ipu6q7gYF3UhRVy4EwUf+GgCimARCzKBWhBf2NpgjekzpElJrJln7r3n4X9uMpNM2oBnmLnn/uf/v/P9//+dM8AmYxgQmyy1zObksPVhLcO6yR2NFnQMUOTHXwGeyY8O5Tt6c/cZrZNBpb40d3H63JFTv5ILJlexLI5ZnceP24CboB7wwIeFwc/3H35qX7a7C4wLGArVkURYb+Dy31fw80dfHT9ydur19YDNeVu6FMcOUiwtbvm0MPjDs0ef3w0/FRnPM2EodRCEGp6n3Y60yua6xZ6H9j7Rd/q78Ns6zpwcHhZjk5Mt1ry5g32+kc/HG70GDD0+PLijoRAkejpcA+PIMHI6+7c6QbXuME+4XjYjRTaLvaOFo5bIwbExZYk18VrAxSL4vYBjF6i43VRPOAlfNG5V4SQ9cEegevNfuCkfRhvUFisi0ZVB0Ah6KIRCidhG4CI1iYD1SKm0bB2mqXnfv/8lgiUCEgJhuQHHd6nOHMJzoeohtnRncO2PKZROfIHnHtwZM72wDtiJQamubz5y/x4mnEePnZn8IDeQUxNf/4iZyzPmwMuH0be7H75H7aRcozBErVLDn+PncPqtz1DdljT95SWrIOwjDysVO5z9xTxHsaS39+aOZRxeGKJ1RtHJXV2YnJ3nv710AneTY+7hXcTaQ/X6ddy4UkODbJmdd8GLIlOpVW3D24YzUSrFhouXZn4KlxuF7dsSr8pIaQlp0pm0SPckUA9CTF24BEOFEvTuDWzFQFcnFubmobQynPmUS9gGzIslxN08/vvVdxcXb33sONQ/YywDpqWErlLzZIR0TycyO7JIEmtTKaMz6UOQr9bauCyWaDswvZlmN5888PRIqM15h8fqkNYzVofrQlDjVBhAKwVODS3X6pBRBCb4Bq4r+LHcitQ8+jqxFo0eJTXZPgnGmLHBWUo7lU4TkATZ4si5G/OWbet9BW7td03HgLTH+b3Zxllq8SmP2RimVCjR1dlBB86FLU1TUbTxymhNmoaVZwvYvpJcVugYM73KzFhLJCl9ThMCYfb5P0YbMAl8dX+esLF0wphDTBf/WYJS1E8CTaaScY3jG4nKYuLStCvCxsZH2E7WDyot2SmIPoIaV6tUEPk+seZIJZOQlIG0jRSkEMopoattl5nFamO8VgqmVmuiNXcQkiCXG/X4jrC19mkTo0iKjBvJHbaZ3Fpkm6UwHJ9YcXMYT3I3oq/N2KhIGd9zTSqZ0DpQgStcFnD/r3dmMWVBiq1SbmBM51zFypipTpBCX+R0TjjdOpp7VB3NGAk8iiRTUvKEzxNSyfpNP/MCZadtHGG3NHJbbei/xtDO/O1y+Mtjvvpmwc/2EdmcL+sJ4fqsEQQRXUIzkotxV4aHxq/On7eglhQBt8am2slTY0ukbes50pvJecLco7nxVKNerizgGgHZewh3ArX2/wAI7eC43hqZkwAAAABJRU5ErkJggg=='
shell_icon = 'iVBORw0KGgoAAAANSUhEUgAAABUAAAAUCAYAAABiS3YzAAAAAXNSR0IArs4c6QAABA5JREFUOBGNlE1sG0UUx/8zY683thvHThri5oMImhKl4UMEJEKgCJACUQlIFXABqQdUlJJDpAJCIDiBxAFKIaW0ai4I1EuRUOgBKlUIoqQGSqNASZEAF4ja2iVOm9qOHdvr3eHNrOMAPtDR7s7He/Ob9zXL8D9NSukllc30RiuqCerjjLFyZV7TsZqVyoLM5e5MffrZWyuzc/35n+YNazEFkLa3uRmBW3qLwb7bY01P7HieGcbcfxk1ULIscGXy2OSlgxMPrsbPabl3I3W2BDgDfVFeUl+gbkuXjD737Bfh4e2Pk+WrepE+/4ISMJrcNz6b/OBwVEoHIgi0veBF4DaO5eM2uI8hdD9H9nsHifcs2FkCCIHo2Oj56OhIH4HJHcCzRiegeenQRCzx/qGot4Wh41UDuR8c2HlXg5sEMNyxk5doftqDum6O829YSLwz3i5Mc5oYNxPY4mvQ9FdTBxL79neqeWS7gK+dIdjHUTjnaBVGVvIKtBCX2HAHh9nJEBkSWn7x7XdvypyM7VUTDaUTNqU+/HintMtoe9GD7DcEosfYxGDn9B5ynZTpVc2xyMUmihzlP3vaQeseD5xSCamPjowQa6OGrpw6PZqeiQl1ev09Qp+emXEt9IRckAIyBaUceUJuKq5O2Yg8KhC6TyBwK0f6y6+9+TPzuzQ0E/v2SbXVSknIIlC/jSP/sws1u7he1+5TCIoXJfxbXWjhNwf1/RxOQaK8TOdJicz0yac01EomWxW0foAjedit6YZBjpVZB4FeAi1IrCWqdMGBv4fpCggPuXlOHrT1XsUoJhLtnOiifDVNuQUaH/OggUrm8jEb5g0cdobiaFKCSOq6z6jMGJiHwVkBfNczXJm0EX6IIzKs7YOTzvg5lYAt/H5dzXaWXOvlqCNg7kdHZ19ZKSiGzCC4zx0X/pQIUvyVjrmFkeWuAcowHghIjTc62i+rhT9espA/S+6Ry9xP1hQlGN18lRihrPUyeMKu1c4qhSTgAnNnHCy8XFIIKsW2RV1ke49//okwfcOZ6bnI8glXqDIq6eIJyr6gBDEKHyNtLlQ46LpSWflaGRaP2EgeKIMxP92+sV+vG9m1rXpNVWwzM7HxC6+/uVvd+a4Jg34eJFaBqWppY6prpYREfHeJ/gGbZcdrr+wP3n3XHhVON7pqH01C9w6MhocGf1dbS0n3p1EDVMLKIdaimgANDw/GNwz0jymGmlfvvpqoJhobF6i7MTdPMfO7tarWzU46n84pLKyv5c66BxtNeo9S060G6ou2/EKSB5aOlrF0tKJFnRGlOBLP+qviwboInpao2lNtNdC6nu6plmd27qhq0EBKJrLfnWpigurxkb4Ueb9uLsn9W7un/ql/zWNKZC+9Pdey4W9Tunw1spRtRgAAAABJRU5ErkJggg=='
unraid_icon = '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'
moby_icon = 'iVBORw0KGgoAAAANSUhEUgAAAGYAAABCCAYAAACl4qNCAAAAAXNSR0IArs4c6QAAAAlwSFlzAAAuIwAALiMBeKU/dgAAActpVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADx4OnhtcG1ldGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IlhNUCBDb3JlIDUuNC4wIj4KICAgPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4KICAgICAgPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIKICAgICAgICAgICAgeG1sbnM6eG1wPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvIgogICAgICAgICAgICB4bWxuczp0aWZmPSJodHRwOi8vbnMuYWRvYmUuY29tL3RpZmYvMS4wLyI+CiAgICAgICAgIDx4bXA6Q3JlYXRvclRvb2w+d3d3Lmlua3NjYXBlLm9yZzwveG1wOkNyZWF0b3JUb29sPgogICAgICAgICA8dGlmZjpPcmllbnRhdGlvbj4xPC90aWZmOk9yaWVudGF0aW9uPgogICAgICA8L3JkZjpEZXNjcmlwdGlvbj4KICAgPC9yZGY6UkRGPgo8L3g6eG1wbWV0YT4KGMtVWAAAJV5JREFUeAHdfAmUHtV15n1V9W/9997q1or2BS0IsJAE0jC0kcHg2NjGI2yHTE4G4jDjGTsO45jEZ85MOzMnYZzMiU9mghPFJgnG9hgZM7HMvrVtQAjRkhBq7UgtqdVaWlIvf/e/VtWb73tV9etvqYUWGiLyTtdfVW+57757373v3vtetZLLM6kQLb3sltsftGzrAX+gV6SU9URZtugKpBWqah8Zqmg3jI97KrbDKvqfeL39ma4lS34v1tGxplRR+0Pz6Fz2mLpFJU5KZPlviNQ2gQcuGEE+hJhrvNi2iOeJHNwp0rVdpGnyZT+s8yF4+TOmMCxSN0701StFqqpFl4pgSsQVDA+MUZYl2omJxOIi6/9OZOE3gnEvwa3jfCS4PMsvf8YI1BQJngODTh2DwipAQoC2UV8gqrIgLZCi+iYRaLmAZfnLk9oXgdWHgDHRaKCyKClkhJEY3JmiPD5TrSlIzr+A9GFgDFcUpJApUFuGOZQkk418k8dyZESSFJR+aH8/DIw5TVxKBC+u/ubOInDD5IfVyJx/AWmsGaNWr14d6phLo87ChQt1e3u7gYG7Kxq6i4SnyqJkRBIT9ULVRkYZ9RY8XlrPl1ersWaMXrt2LezWS09oz8ahnqI8+PBdwBQs8KqQE32OxV8lYFIbBmKN+QDX/iVLlsRmzpzpv9dxn0mxsWQMlQj1zJgmnaz2FQleVSM6jasIc9m2NdaSUGnhZsqrRTJ9dEJFkskxxeEcwEz/HR0dJVzS2trqGAk/R+WLzR4LxoQEEr38Y7dfL5b+ogwP+JLp8ZSyqXtAVSMAqEe141HviN84jbgqOfyGlsKwEvrzPt4V7vxloSsFPXBslU7ViurrFV3XoCws7tr1I8UFnqA6HEydzYicOCK6Yb6ofD+bv58+DPHDOESWfOpzV8rEpoPta9ZkQ+ZQY5gyll9qGgvGiLS1KVyct0tjsfhX9fhp4k1dEOJEHMu8wyOYA+LaQ/3IRdmy3xKhcwiNVV4notFgPfEz/eL3Hdd6/dOiq+stTasLzXTAOgNLw38RF5LEsE3TFJGjRyMI78sdDLApHctvv/N6PTzwqHRlN7R++cv3tT/00NBYMWesGGMIoP1C3s2VJHf1R6U0blLR8kqgmMKUDsho5hEI6oMRyc43JW5Bcm64NSCeD4JTDiI+ks1kWP9JJS8+ZuXnLRGvrlFUCaGvsrygKesxfIa86gM7RG16TmTG+xeSCQnvrvjsZ1vcwcG/jCUSs/zswKzszt3jlt/5u/e2/+x73TCAbKw5VBMczSUl6pYxS5bnQSWBSDV1YrkFWxXztnKLtirwGVcJz7msDVbZflW1rWsbbG07tgwP2YJyKeRx5cJ73taFnIW1xZJ0vfjVdeCHhQt6DpJk7uaZ3j7Gj8XfrwXjclhn3r81RkFSjHFTGhz6mu0Vrndv/Lzr3fq7JUd5t+re7T9ZfvdXptAQeK/W6dhITCVrSTxYTk5hIFAvCmLBWR2qHuWWsMpAiHAnE9UgCHkCqodhF9YzEhCoOzBCSU29kRALIRmL6oqxMqou1mMic6AGvWrUY2jGBpz3KcECc7jYL73nD2aqLb9YLUs/J3LlEl8lqhxXi+u8+Pcr3MPb/mH5V9ruXPu/2wZDybkkK3VMJSagBwiGGa0TSdFxc2kdT0TPwZ1M4FoDohqGJKvMjJckTF5eNH15MZ9xMUiEBhP9AF4FLMJNBPmEabgfMozIMIg5hqmmpiYAfuSdVWInZvtz0UEiicH6llq8Urk33e07XnaV3v7at9mtMaHb2i6JxpfU6LxjJfoeTCyuGz7UGxdsPpuFm3dWCAnIZy78UZ2gTVCf+eV6IDvKDMxKOGivzHsIrxK5sYwsg8CROaxOdi23p14tMm5isD9UKmixlK2uudH3ltwhauj4fcs+8ZkvGlRgFOFu9EUlaud7vhjGEPiZF+HD2x+lY0DmggzJAGK8s+k5kikLQZs2Yf1yftgO72VrrAwKK9YZ3fueazrLz+yLOg2Bj4p/GdK7PbSG0YjlbX9VK9kjs9X4GfCtaj1MOC56ULFQzfGkLUtXudb0j8Bo6fnmst/+j02AqdtotV5kurA1BrNldWcngMMrp2O+OuwFz72trWrfvgzKOrB0GFagELTyg5mMX7xy0vAKn807YSCPz+YKJYnPUIWBBEVtT9elsxmYzIQX5Y+QQuUVCUCkubeXd8tMnAhvcw8GcDGWUyYzF8i0i+4+2ATrc7yuA82jdZGdWZiAxYKShgnKu+ZmsQ53LvIO77kbJX8Fxmi4ExZdClYdJZ2Vfz7GABlQr63N53jKqfKlvb2crRwHbjeacAbxbp7DO2tF0sA1yKwxwZ01grrmIfwhHDxi/Q/aAaYRjvA9qnoaJtQJ4Gnt2TOnGw8TqscEZ4IoDxpEeJczDBD2chZhIvDR3UgfVKMa7q8RK56WBNY/GiGmKeSYmsGoY89SM+Z7ato1tux7867WtrY17W1teUic3Y7pGjYgWPYrbbza+IyngHEGl3djTIAwOH39KxvneZZutnxdpFQAVjlh9iobeW5V9YDOZRYqryR0+IoTxotldhtBUEpBOcHBj6fE7tkPqw3i34DdSVpeZoBBl6Yq2zhxEALWXT5rjIliTQP8GFplqBeBNNhAxdm2pXsPo8xJ6863blq+atVeLU4dOoGpBn+onICfbSvLJxdLeza8+OKxctEFPMACdDBi2zCFk4J4KswY0oXMoRpN14mesVjUrleuzm3cshBgO6L1qaILM4I2Zpz+oVQZZ/2cjGkNvdsl69Yl/abxf2Zr79N+rr9f+TquLU7dIJEunAZ2YVBry4rpRFriW34lTk2DbRbqcGYEtTkIShPo19sNwjsC38fcjXEQVDr9i/ELzenBE5Lc/Cvx0wjN0DiIEjsHQdCvKM9zrFNHER0YN9U60fUDlDBucxpRZBge+qCkk7B0Mp0SK/YlZH8fFxMRqwBu8s76ceOJouWD2TTNKSFkjgemcLIwkVGYmLpliqh0Y7V2i0uX/N4De539m5bjXMJk8UuYLIp0z2nLOS52cr9XP2VPx9o1mIHov60NN0wv/o6WMhmuG1jTFnxU2V0bauwpsyV/xc31kkKwkEgRoSgRGZi1CvEqZ9tr2p48U9kTpwWTlXVMVfwEsytoi4H4mOElmtIYCH2RsGIEFTPbAdi4xFBuT58vdmPzKDBBHA6DM3V7QXvpOsube22VIVrUXwQR74TpnDwiiXc2i5fPJ6IiQ5CAKOWsyofkvgYMEkNI1Q0ikjqockOiMalUrEIay9pE0zEWHYO6Gzz6x07niT/E2KeqeAqdI8CKiWRoWMyBPQMZZ/jYvuU3/etfqnjisdeff/5VdOOfkzERUrFZc7Ta8li+tHCF5KfMzoGAcUgN52nIGRIcZqwd07qh2Up37bBkztUIJoKIJezPVzKQQDnjcajCghOKYUlhxkI8jxanJxFj4o6bJA4kQeYuBlHSgYNppM7QKUQTOIBA1vCg8vpO6Nykab49PEQJDnFkXeKJeyzme8mU5ezdYku2DzPswlJNzW7TYfzKJb3e+poe6Tu2SHF8xiczghn2RXiUICOAWprnTGXcsFQ7TryqWvFjmAuUcExEq5AVJ9NXE+s9dLV9ZOfVXn7ovmW3fuInvq+/c17GsBtocIsOnpPpt+1MH6Y3OjWzkYXAh8RGngdVY+JbQFj1dAWMIYKsS8KwLsp0Q0sodZY4g6fE7j8RtDP1UJf1DHzAJDM4mOyQiTDD8gmcTqoRJuJCCa5tCGai76rYqV7b7jsOmHQ6kSJc+Wg7SscQpUMczvdK6OjCEtYIirSsv/+u3NKVy7frnt236sFTjkrXARFIiHELwBAOFRapBs65G7+o8uMm+151HVxQkPrMSUqAGIddyEu8v9dK7Xojke7e+tsFTHGy9QJSRFyiAP1pYbkHwc0FwkTPpL0hAgmBeiMvwCCTqLZ4ZzKMwJ2wgHQZHmGGcAN4IRPOgsk+AItrkWFmVC/oJ8IruDPQSVxRl8QzfYd4EJfzJ81NMVOt6Ypfe4e3Fq1jBwGAUx8wzdoHAhAPZOViKcnMuAqS0sRM2/JcGyGl4ELMEIYRnkvm8pJVVm7STNera9GlzAnQx3niIjALO2XHWFQD7qM53yNpMJzhK/KoRUzd6M66wRV5O6Z6uU4Iq/wetcOdabT8cl4FHkHl89Q3lS76hzuVbJSYPPtlSdRvtba/JnrgFIwJSCbXFzCbwdVCoSBDuRwMEhfxPUglmcaJYCYEAERD0hCtkHZVB3b46Z2/Ur4dX+fe2fYoRjR6KseFouIQmHmNZnrZZo0q4R7Vi+qUZ2eEFR1PPlck84ofk897WBbdI6DldmGd6J33cl22rXiJHivrVnRdfjy381euwocbblideuW7D/apcdP/l7v7lbzVuSEuxZxLCxMxV2ywFiWThTuHRCadNaFYYHCB2wC16sWTfvLowUJtx1MJr6/nqNc0va3jvutKXGNoN0fkZDPj6HSnUpBPcfPiWtDKZjaYMhKJdjsXOKbKzvkeEWJE/kgEKTEjOozqRu35TuR5NykEGtUzdxawHFeUb+oyK8w3ZWwbwYnKgorQglGB1draarW3t8JcDcoY6ejt7VWBxy8ys2NNtK8PUwrac/6Kl9xibpt64v7r/Kq/1dZV/0pcbM5mhoagyaDdoDFgIp2mBxsZtKhOHaptDfXmVndtV2BK0ju+d1gap/+Hjp89uok1yRh69uHI2TpI1z79tLsXjwO1Ba/Gc4P5RvPQWFoUtApimcUfvSL6azrnO51H4wyiblROgmHxNptdUXuIu4HJxTycSUbl8Z2qj5tlbEdzmgs/+2fE+czF34VpykQYcDMMTPYRwYx4AFwYkTZVXRedmORjccdze+jsnQ4SmDxUieKhS7/cNkH2bljltn//t+AHLfQW3i2qusHxQKPBoSFVAnyYvXBI2Dcakhn44SPGwdnswUn2E6dOWFVd22LJzpcw+4cP6vpp/2njusfWsVobBIWMGTUhemGskO77789NXrLIUyCGB8tHV8FKMr2YH7RFVyBSaBTgHcSEJaW5sRUxkcQJEaQFpavhKNISw8zxeC6ZIX4zy9GcYFkXbehzGIsLr8abrm8OYJoFPOqfhaiObQZ1/LCZHC6jCTRjaRiYQvyEMH2sBzYiCcYIqR2PMEJnUGe0X6wb13zrO3WJPTsnydH9C/TA4RXy6vdvVlUtV9tzVoo35zrsxyz1/doGK9PfJ0UEMikpMINhHNklMyaMg04xFntl5YecWKbPSfQekljXFvGP7Sq61S3/pFvmfGvj4/9oEAFTLFy+c92tt30BXvNiK3sih5kd2N8A5NNi8OBgVDVUSfbUXH14r8Tqmm0fBDDEighpBo7OQUSFzSzVe0Dk0F5RV8wKpKY8YFDGMAhqDOah9OwT61iX2JNnBExBn2XmRDAhLcaUProf9feLapoQwCSRTSJMtGPfQ3CcD+0WC0R3Tk0LcAz7M1UNHxFOi8WUc6xbdH+P6PzgncuWXTVeeYUEKIklgYsxzhkg7KL8UrUsntCCsM0V2q6eKemWKc6URSKT54o3aZa4U+aUgA+O64g1BKbkseBTUuInj+iqrb9UdiIJzxiSSY0AMlrZQaifY6JPHcT4Bw/4VeNe8ybM/79v/nztz4lfsKm2kJFoI8Vq2S0ffz2eqlqOgyegC2cYuiLRDeFJASxS2FvR/PFdVAjrBCIQ1I+eQyIJ4mUAgGuURLhkAmcz+6OK4jOJOGob1oXkUDUavFCNVc9MbH8WTFaK4J7RyHIwqW2zSXomKCNNMUxAeO9SDS0B59CvH4e43gRX6sdpnaq28c2OhSMOWFMyksOCb0GKIeG6dku7Sj3zR56OT9mJ3dSceFC94J1ykr06Xtulq5u36caJHRt//HdlUaUZzp3RSjwcyQ/GixPnytBVra7vOAr6Gb5XTKqqoLMNc0x1PmHVwuDMLKwEUfmMWqwZ1assOvPZEDmsOyqlowYXAbPS0T8XTMMnA1OB5Xw7g2PIAW4ggo8Zr7GTqnFXiBhwRjqcVJZfEr/owSTOgilQX6hPpjg4tpXs3mHrcSs7CvM/+vm4XcjoYTc22DJueNf//AY85BGhO6k4LDiCKRy5o4rZKq+mSYYnzQBCMBUgeqk49HNNDeBgAEzlGFD4HuSe49eMHLDOURxlR+RgPTKSif1F+UFO+HsBMMvtyg/vAo9goX6D8Y2OqdYwnViN7MPFiAWZAilnHDQDPyVXoKQw3M8AFeKiPfss69gehpoe3fI3bV3spZy+/YB5bMXBQDzwcmFwmMOC5ToVDw7iUePRrdjFIvUJdmkBlojE0bZMKGBYJh4nzlilEC4tL8LHpDDq7VLBEwZxptHAL8/MuvWu+I7OlDP7Dxho1JUHy3QoOxxICiQUPpmCptF2LqOTXVstv5jdV5i84GcEASYkEQz26BM2NzfrtTiXLe3t+Av2iSTYPCP5z0rQXQJ5BV249mGa0/YOPHOUcA0gk6i7TdwJeTypwjyD7IWNa2SvZAY7xA+tKzIFcTA6aOYABi05iltIjJFtz/FGWLxMpBdtEfk1BzmIs9kTCvG8GJjlrgib6Cgp4Z6B6iqUPKgaVCCtWKwcnerZp2KHO8WNVz/y1tpHYB7C0G5tLYL4JLziCZvVmCprcVBw5R131BQLhakb29rK6wzrVyasG/5x/FBKAIAyic7wiP7AFxCONj8Xwt4eke49AZPor5B4Bis2M03Dd2JaeUXlYR2244ymdUfCncQeSvvjoje+EHw1RtOZ5cTAwI3aV8KsLMMzJw7hYSLprh2in3lE9J63AsOC+WQY64zA9wJwNiQBWEyagrIld+SgWICPZV48bPb5oI8fT2gnl/Gr9m2xvOzgUdU0/Uck8O23355o5TkBSgV65uLOUzPLbr11RilffAwL3L9nPaaFq1eDECSMuZglavnyxRv9a++4rnflpz3txM0a4yC20JCuwr4fDLGBk8ZUlbd+aTasZMWnRWZdBacK+z2GgIASMcKABKFMYj9InKVmpvIdZVRXeZzaJ9zD74js2CCy/w0wCQRcdDOuFaImTDO+kJEowyC0Yx98jnA3cM2YjeOp+3tF9m4V2fyiyJFt2PCfK7JghchMmLhNE7FpBQuLE4FawMDELYJt4PKdKcQ3whmTozg0KMWDeySx+SVxThyQ4rwbpHDFPCk1jNduqkbX7HpTpX/1A2zYOfdtePnlNQGckb/X3XbbPNuXO6GR/q0TS8x3S8UjWJ1+8/UXnmkfWdMMUKvlN67s8qcsmjZ87cd8fGAKJyirrGJOJ3HQ2+qH3d29KxgoB2RxLYBnOx3nqaZjwM1XBOH2KDRPCWM98oCzjaYwzVzut/AbSp7GZzj++CHRRyB9x3camKoecLgl3bcf8KaImgX4V1yJ40GTYIQgnE8pMhGAkKhkLlXecAanUQCP29T73wKuiGakcBqzGu5HFn1luvFh7TRRE+eJjJ8ewMOXz8YM5vk1OqGcXAZnIE3mRzjT14LvoSHRPr6EtvZvwr4RNsdYvwgHNd2svYnzlNc0xYsd2W3LiQMFiaf/GGv028AyDQMhiUP1zdryZ8EyWAyKXAtrF3vjCnMTwU1IMO7QueohmHk/qioUOrH2YGBBoh8Dz8iO+8lamik4IYmTHhx0KQ88wQTOsmQ1CAOVxuSijAhjcVXYRpYqSA7tfT7ToWIIngmLpFmPuEtHTzsPIuaHcVIf7ZEU1SPbYDMsWPRBGKobfKWs88QXgawU4KbBGGwwGeaQKGQ48WMdnAfQwzh3AVwV+8ZXAUbKyDj6PpQEEFFjQ8oQHO1VHG4Ax8OdWB6oMDiTOeifsOmDMfTDMQ6dwoTKUM2jDXYkTcgJONJA4mTzClrlB0CHaqWdZB+Igo7M5w0MvRABDFJIODwTiGI5CcAZhioKCLCq2ov7BuSsR2dvgkm74OG6j2J79J7MlKskVzcOgTUc0EOpJOJKpUE4Ilypqvge5ZH47M9c6GqESuA760Z34ELCsy3vTJVwg5zTZZHE8V5WY1GlEK6RYkyECO67wTNlgBXBK9cF85h4I66AqSHlOhdMoGCvJ8KXuJh4l7ixuKo+1ePWdW2IeYXsc76d+iPLH/LFJbEFJ2YpjBpeOWJjrlVybR+nNC3LhRhhqkvJcrXjxzzfduPiShVCOSC9LvpxCzMOnNR+6UXl2fcgsKeG6lr8GKwubhzz0xaLKooSYAjD6hUpYlBF1nkfgS1MC8I3VQ0dIibzJcgOwFwofNOGgMPGhGMozLwAlPklPKboHrydrhMW88MonQdT4F8GYCpgszmAMt4eL+VLqb7umD/cP6TT9d9688nHN0cgx+KOuETVHl0cyiQHjtXE8B8leGqFnWtoAzJH8eR8NOhL7LGS5nG8xEAcRqVAAjO1OB8raXiJ3Vx6MzILkqRzUE+MfhOZMxkYZIESCsZxyW84sM1JHt0mJSf54MYn/+k1dk7ragEkhNsF9FuYd6EJFhvrYzYEyYmnJ+10B3bvig2fvM4BUjiegw1+CiC+sGP4nEwhktE9ankRd/bIi0wZAkeOwQ9IgumTbWQgccULnszr+/9DZCo61IgKG6ZQNbMgCu2MxASCrpUXi+n64wfcmqOd8ZK2n/FmrvhLkedMeKVj7driOR2TkbDO9RZhpa1Xf/4wVjfnl85QrySz/Sa0gCAro8yYzh6Cq1gMR5k954I8Wr5hCgq6sf1xDJtJ16aThhnv4CMnMoXmAuu874mdREwpSwlM92GsyWQK80YdK+QEDT0YQunBk6W6Ax1xLzfY7dVO+kbHmjbzid+ZQchLHEuEoaGJTJpzpacKQ3dLqt7O1o/HAmMYB1wgOahqzk4x7xKkhiorBV3VhWVwCr5Run9ei3x6dr18Zmoj3h15/sSw1HM9w0gox9GUucSBjd6MwzUDCQmPd7OWZGExcuIxjcqQsAjVXTumEoVssWnvhrjV+46PKPGX3lz32MuoYXV1dZVVUNDivf8ac8Ofcf16mMbrsZhJMj/ke/BHyioM6kxjr+Hcs+ncSJAeVF95cAcWh9wzp1lmxzKy+dknZEaDI3evnCt3NiblACK1aagP8n1ME+GZyYR7SHiqZ41Y1/mlJMCEWHlY7GNuodS4ryMe790lflXDf3njySfWsgb2UTiXxhrzQGKOdLSXpsyZG7MKmU/5iXqVwzEa7LoF6gx61fgAZBZmvEHhAqc1o7C1WEfeyZdkcXVKbp1aK2+99KT8edt/x9bGZGlqqJEq+CrPHR6URkTVqdbGLEXSHUkC95TgNGpEhd9dbZ3GIGIK9+ab9m2OpY9skVKs+q83PvvkN1mrFZHip556igvTmCd8orCaKh4Huyc9jl3LrdW976hUNoOTwDEyJ5hpxmLBgDDbzMJ41tSGDkbe6YsqEITAPIKNA7GJy0Ggn4VkzLoSHj3Sq08/IX19A5AmlINo2LIam2kX4UYfh4m4w/z1h+G152F1sTxiVlBjlF+zphhJMUzp2uJUH94kJZX8UbZ22f1swH9SV+mpjwLkPWXZ2++6S0l7uz68863c5LnzXTvXd4eyU3a2YQLFk6MzQzGBTS6Q9GuwJphcFuKigsVH/TjFjb0KOnuQLhshlKqYY0zjFmwsHcoWpA6BwKtnT5fbPnm73HjbJ6WQHi8/2HFUjqCHBsAsXgjN0NdZyTADDKYks38mMgT7JYEJXAxHgbLzMQWwOEVcJ65iXrHUtH9zrKa7Aw5h8qf5iVfdu+3Hf5r/IP5zoE2mUCS5gKV+4/c7U8e3fyRZGp7jpZtK2eoGsMiSJHY2bYQzGOpmnMFBjAnf84uDvASuFBbxNOpxnaiCpMS5NTA8KEePHZHDuztl0q71MikRl+etOhkcLEhL80TpxgfK3995VN6GZTYXez/DWIdGt1INmc/+4YzgtCCheUWNMXnMwm58koghYZ2zoZyZQ6iK1leikCs2YU1JH94sJTv14/yERfdu/cFfDH8QTCFSwDhI0Re213/8zo/o4qnndNO0psz4ucUeBAkG4G+2xGOKEmHUFdcaOJ6UlCLCF4M0DrDNagKViMSaTycQZ1peb8mUCc3SI7XSO/0akYnTZS9DHflAJVqpmMwCrOzFMMWQLkSaDKG04OKiTgtLl3CnCmY6n3QEtYKqAILx4SSko6syfcWG/W8mEsd3IPRS+7fDdcu+2rm2rfhBMcWgXsatYjft+ts/+SW/kFvjYDluaJlQKhaKsf7+AQSf44qfgtMY4D63DbWWgLqqq62WNOJqVdgqqK2vl8ZxzdLQPF4mTp4kdU3N8uKeU/I/dp6U+bCbeUItgbakbx7P+Kz09OwoI1PxwP6YIiLzzqzACTYMYWyLPpdhCMujuqbheX4An9h4DKZCI9eeOuzVd3XE5WSX9lNNbRufXfcnLPggmcL+yhLDF6q0aEFbessnvoNzUr//sY/frK+7YTnsEtcp5hFNJUdMQ0Sioc8dMKY6XS21tXWSwgGOBDam4nGc3YJ64xkrB1bZ7oO98jtPb5NjIMIcxzISEnQMGHyIiE/ARCkoNG9lIrMOLn6TEkSuYfZGzGDZxTIEzKD086A5mRIv5oq1PbtjtT1blTfcf9SvbvrDjU/+v0eJxAfNFPZpLDI+MHGdidabz33tKy/v27ptrud6i6bNmCZXLr7Ka54w3q5rbNRNzc2qqQVSMW6c1DU0IOpfjQ3EBLY3wBAaBkg8O1CCauFx0Tp4+i14f+5gv4xPQA4N4ckUMuEclwECgnPNoBPI4CJVJhZ0nKwLJIR1Ktvz/QKSCeOD+1xL0N6rGTjmNnVtjlcd3oxz4O7LunbiPRt/8dNnCIr0WL/+cejHDzaNYAy7jpjz2He/W/rMb37h+XVPvbBg0xsdV9bXpK3xEyeUoL7sYj4PWpU4CLPpQwbwhHuOJ0ewO8lnnkr0oOtLmNUQLGmsiuN/8AzKr/tyckWc6wpOnEQqieEB+hmUhnCtCBhBZoARZAzzuXZUSgeZchGJEsLkQ0J8/GutZG6o1NC9I1Z/sMNWvXuHce7r2zJ+3lff+OnD+7klvLq52Xq//JTzoX3OkXGmUK098OCDdU/+4pm/Gc7mvvBvPn+n3HjLqmJDY0O8iFkbHJ4OJCTqiCH9KKwfaKVAMrgW7e3pkwdefsfEy+YnbOlHNIDnDYI1g/eAcOV7BJT3i2TC6aZUWUEXWNjNYe54PuvWnOy2qo/vta1T+8nvF3RNy5+9sW7tS2wXqi5KSYjQaWgf1NNZEhN1HEnOD7/3vdz/+Ytvr9u0rbPq5fZXV5SyQ3Z9Q0OxEWrMcRzsEkDVhAQ152xAwMo74bGc0tNYk5S5+A8fz+w/JScgSVeg9xzPdaM8ms1mfalUT9FzhNgF3o31yL7RHs4yz1b7MIHd2t6D0nhoq1PV85YlA0d3evG6/zY8b+U3t/zwoV0E/c+xnow2pHNKTFS58vhm66c+8ztv79r7pwvmzZ646rZb5NrlS0tgEPbmfBxgL4IWIDAJiRTcToNnGfe5mb9pzzH5z+sPmvk4H/9MYgiSAyU2Ys03QC7qJ5AMNiEzqKpo3ls42pvKDvqpUz2xNGKBTn83Pood3K/i6YdLDTMfwdfCQCRYS8zZr/f4ryMJayzSacq9C7RIrbHKZ++9d9HWzW//12y+uPqmm1bI0pU3yLwFC9zaBjgtoK1Zd8z29NkAwRsYB4FEbd9/Qv76jYOyfagks6uCQ480nc+vO8IauEXIc9ecSpHMIFPADB0r5vzUYJ9KDfTYyYEj+C9POFRRzHfi39H/EP9d8CcbH394X4Rh5eSL8v6579HYzotHJXMw+y34Onft2tv1By2N9cuWXX+dLP7INTJjzmyvsbmZ5jKPqSHU5sOo8owkRR1EkmPDlD50fFB+vqlb1h7ESX2sOdNjNjwnrlGoHWFWySmTFxTwwx9KBIrJF/wDNFfHcOgjMdyvkpkTViKDT+iHjiNGNgDPV7crp2qt1zTnmY1rHzoa4RIyhMIKfXp5pWj4F4YVLJVWHGKjUcAGX2trq3/h+Zc+d/DIiX/XWJteuXDRfJm/aIFMmzVTJkya5NfW1+KzFfwXDDo0SKRxxDCqPPo4A0N5tWnvcXls+3F5e9jVLVBtOAYSfJwTcgdSYNjDH64dYIe2Yak5pZyK5YZVPDeg4sN9EsuexOcOfeLnMggje5txzutZlap7dmj5kk2dbW0w74JEhrwf//k1gj8W94tjTNhjKD2caYZgf/7II+l/XPPwR48cO/FZhPpXTRjXMG36jOkydcZUMkiamseZiEC6Oo1vlFI6hpORcEAx6S0ckbYVDAPr2Klh/fru4/5TB/qkH4ZBCvLAwCmiu2LjCwQbx6psHFNycBzJwREnB8eh7Pwg/jFpRnweZfK9Q+DfFny2/Qo+5X4lO3vF1s6H2syJk4hQxBuX3xZ+gxLlX473S2JMOBCFQdqR9ESD+9jq1VO73jl0/UB2+MZi0VuajDuza6vTTY1NDQIzW+rqaiUNh5RRAjqk/K6EkpOMx/BRaUG27u+V3kxOkoo+TRHn3Hhh8wCX5lk3twht5+MYp+6G/OyGEnsbEdYthWT99s3LHj8kbfy64nRiDJCHI8z3ldI2oux0rcvv6b0wJhjNafVWlqBomF//+tfTv+7snNZ/amBOvlCaA0d0uut6k+FPNvnar0N0B2EzVYeYZjM++M1OqEmeqKvG/2qxFHYANI5uWhAJwT8dU734xzBH8N6trPghnAjtdlItR815haizkXcLk8a6nKyskeid/+3/AwxHo0pG4T8lAAAAAElFTkSuQmCC'
dockerps_images=[]
remote_enabled=False
local_enabled=False
ip = ''
user = ''
passwd = ''

class c: 
    RED = '\033[31m' 
    GREEN = '\033[32m'
    BLUE = '\033[34m'
    CYAN = '\033[36m'
    YELLOW = '\033[33m'
    WHITE = '\033[0;37m'
    MAGENTA = '\033[35m'
    ENDC = '\033[0m'
    GREY = '\033[1m'
    UNDERLINE = '\033[4m'
    
    
if os.path.isfile(local_path) :
    with open(local_path, 'r') as file:
        tmp = file.read()
        if tmp == 'True':
            local_enabled = True
        else:
            local_enabled = False
if os.path.isfile(remote_path) :
    with open(remote_path, 'r') as file:
        tmp = file.read()
        if tmp == 'True':
            remote_enabled = True
        else:
            remote_enabled = False
if os.path.isfile(ip_path) :
    with open(ip_path, 'r') as file:
        ip = file.read()
if os.path.isfile(user_path) :
    with open(user_path, 'r') as file:
        user = file.read()
if os.path.isfile(passwd_path) :
    with open(passwd_path, 'r') as file:
        passwd = file.read()

def run_remote_cmd(script, sess):
    sess.expect (r'.+')  # This clears it from previous command output
    sess.logfile_send = None
    sess.sendline(script)
    retry = 2
    while retry > 0:
        retry -= 1
        i = sess.expect ([pexpect.TIMEOUT, pexpect.EOF], timeout=2)
        #logger.debug('i is: {}'.format(i))
        if i==0:
            #logger.debug('result=%s' % (child.before))
            if '' in sess.before:
                #logger.info(c.GREEN + 'docker ps -a completed successfully.' + c.ENDC)
                return sess.before
            if sess.before:
                #logger.info(c.GREEN + 'Expecting prompt.' + c.END)
                sess.expect (LOCAL_PROMPT)
        else:
            break

    if retry == 0:
        die(sess, 'ERROR! Something went wrong')  

def run_script(script):
    return (subprocess.Popen([script], stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell=True, universal_newlines=True).communicate()[0].strip())

def escape_ansi(line):
    ansi_regex = r'\x1b(' \
                 r'(\[\??\d+[hl])|' \
                 r'([=<>a-kzNM78])|' \
                 r'([\(\)][a-b0-2])|' \
                 r'(\[\d{0,2}[ma-dgkjqi])|' \
                 r'(\[\d+;\d+[hfy]?)|' \
                 r'(\[;?[hf])|' \
                 r'(#[3-68])|' \
                 r'([01356]n)|' \
                 r'(O[mlnp-z]?)|' \
                 r'(/Z)|' \
                 r'(\d+)|' \
                 r'(\[\?\d;\d0c)|' \
                 r'(\d;\dR))'
    ansi_escape = re.compile(ansi_regex, flags=re.IGNORECASE)
    return ansi_escape.sub('', line).replace("\r", "").replace("\n", "").replace("]0;","")

def print_containers(input_string, local=True, size=8, sess=None):
    global dockerps_images
    if local:
        print c.WHITE,'{}'.format('    📦 Local Containers ({})'.format(c.GREEN + run_script(DOCKERPS_CMD + ' | wc -l')+c.ENDC)),c.ENDC
    else:
        cmd_output = run_remote_cmd(DOCKERPS_CMD + ' | wc -l', child)
        for line in cmd_output.splitlines():
            if (re.search(r'\d{2,}', line)) != None:
                num = re.search(r'\d{2,}', line).group()
                break
        print c.WHITE,'{}'.format('    📦 Remote Containers ({})'.format(c.GREEN +num+c.ENDC)),c.ENDC
    print '--',c.WHITE,'{:^13s}'.format('CONTAINER ID'),'{:<31s}'.format(' IMAGE'),'{:<22s}'.format('  COMMAND'),'{:<28s}'.format('   STATUS'),'{:<20s}'.format('    NAME'),c.ENDC," | size={} font='Courier New'".format(size)
    for line in input_string.splitlines():
        if '--format' in line or '{{' in line :
            continue
        split_line = line.split("^^")
        if len(split_line) < 5:
            continue
        print '--',c.BLUE,'{:<13s}'.format(split_line[0]),c.YELLOW,'{:<31s}'.format(split_line[1]),c.RED,'{:<22s}'.format(split_line[2]),c.MAGENTA,'{:<28s}'.format(split_line[3]),c.GREEN,'{:<20s}'.format(split_line[4]),c.ENDC," | size={} font='Courier New'".format(size)
        
        if local:
            get_img_id = DOCKER_PATH + " inspect --format='{{.Image}}' " + split_line[0]
            output = run_script(get_img_id)
            tmp = output[output.index(':')+1:]
            image_id = tmp[0:12]
            dockerps_images.append(image_id)
        
        inspect_cmd = DOCKER_PATH + " inspect " + split_line[0]
        if local:
            inspect_output = run_script(inspect_cmd)
        else:
            inspect_output = run_remote_cmd(inspect_cmd, sess)
        print "---- 🔬 Inspect"
        for inspect_line in inspect_output.splitlines():
            print "------ "  + '‎‎' + inspect_line + " |  color=white size=11 font='Courier New'"
            
        log_cmd = DOCKER_PATH + " logs -t --tail 20 " + split_line[0].strip() +" 2> /dev/null"
        if local:
            log_output = run_script(log_cmd)
        else:
            log_output = run_remote_cmd(log_cmd, sess)
        
        #print "---- 🪵 Log"
        print "---- Log | image={}".format(log_icon)
        for log_line in log_output.splitlines():
            log_clean = escape_ansi(log_line) 
            print "------ " , log_clean, "| color=white size=11 font='Courier New'"

        if local:
            if 'Up' in split_line[3]:
                print "---- 🛑 Stop | bash=" + ME_PATH +  " param1=-s param2={} terminal=false refresh=true".format(split_line[0]),c.ENDC
                print "---- ↩️ Enter | none",c.ENDC
                print "------ bash | image={} bash=".format(shell_icon) + ME_PATH +  " param1=-b1 param2={} terminal=true refresh=true".format(split_line[0]),c.ENDC
                print "------ 🐚 sh   |  bash=" + ME_PATH +  " param1=-b2 param2={} terminal=true refresh=true".format(split_line[0]),c.ENDC
                print "---- 🔨 Force Remove | bash=" + ME_PATH +  " param1=-rmf param2={} terminal=false refresh=true".format(split_line[0]),c.ENDC
        
            if 'Exited' in split_line[3] or 'Created' in split_line[3]:
                print "---- ▶️ Start  |  bash=" + ME_PATH +  " param1=-t param2={} terminal=false refresh=true".format(split_line[0]),c.ENDC
                print "---- 🗑️ Remove |  bash=" + ME_PATH +  " param1=-r param2={} terminal=false refresh=true".format(split_line[0]),c.ENDC
          
def print_images(input_string, local=True, size=8):
    global dockerps_images
    
    if local:
        print c.WHITE,'{}'.format('    🖼️ Local Images ({})'.format(c.GREEN + run_script(DOCKERIMAGES_CMD + ' | wc -l')+c.ENDC)),c.ENDC
    else:
        cmd_output = run_remote_cmd(DOCKERIMAGES_CMD + ' | wc -l', child)
        for line in cmd_output.splitlines():
            if (re.search(r'\d{2,}', line)) != None:
                num = re.search(r'\d{2,}', line).group()
                break
        print c.WHITE,'{}'.format('    📦 Remote Images ({})'.format(c.GREEN +num+c.ENDC)),c.ENDC
    print '-- ',c.WHITE,'{:<45s}'.format('REPOSITORY'),c.WHITE,'{:<15s}'.format('TAG'),c.WHITE,'{:<15s}'.format('ID'),c.WHITE,'{:<15s}'.format('CREATED'),c.WHITE,'{:<10s}'.format('SIZE'),c.ENDC," | size={} font='Courier New'".format(size)
    for line in input_string.splitlines():
        if '--format' in line or '{{' in line :
            continue
        split_line = line.split("^^")
        if len(split_line) < 5:
            continue
        print '-- ',c.BLUE,'{:<45s}'.format(split_line[0]),c.RED,'{:<15s}'.format(split_line[1]),c.YELLOW,'{:<15s}'.format(split_line[2]),c.MAGENTA,'{:<15s}'.format(split_line[3]),c.GREEN,'{:<10s}'.format(split_line[4]),c.ENDC," | size={} font='Courier New'".format(size)
        if local:
            if split_line[2] not in dockerps_images:
                print "---- 🗑️ Remove | bash=" + ME_PATH +  " param1=-rmi param2={} terminal=false refresh=true".format(split_line[2])
            else:
                print "---- 🔨 Force Remove | bash=" + ME_PATH +  " param1=-rmif param2={} terminal=false refresh=true".format(split_line[2])
    
def print_info(input_string, local=True, size=11):
    if local:
        print c.WHITE,'{}'.format('    ℹ️ Local Docker Info'),c.ENDC
    else:
        print c.WHITE,'{}'.format('    ℹ️ Remote Docker Info'),c.ENDC
    for info_line in input_string.splitlines():
        print "-- "  + '‎‎' + info_line + " |  color=white size=11 font='Courier New'"

def print_daemon(input_string, local=True, size=11):
    if local:
        print c.WHITE,'{}'.format('    ⚙️ Local daemon.json'),c.ENDC
        parsed = json.loads(daemoninfo)
        json_formatted_str = json.dumps(parsed, indent=2, sort_keys=True)
        #json_formatted_str = yaml.safe_dump(parsed, allow_unicode=True, default_flow_style=False)   #Use this line if you prefer yaml display
        for line in json_formatted_str.splitlines():
            print("-- " + '‎‎' + line + "| color=white size=11 font='Courier New'")
    else:
        print c.WHITE,'{}'.format('    ⚙️ Remote daemon.json'),c.ENDC
        #if ('No such file or directory' in input_string):
            #print '-- N/A'    
        for line in input_string.splitlines():
            print "-- "  + '‎‎' + line + " |  color=white size=11 font='Courier New'"

def print_refresh():
    print "---"
    print "🔄 Refresh | refresh=true"
    print "---"                   
#-----------------------------------------------------------------------------------------------------------
# Handle Inputs
#-----------------------------------------------------------------------------------------------------------
parser = argparse.ArgumentParser()
parser.add_argument('-s', action='store', dest='localstop',help='Stop Running Container')
parser.add_argument('-t', action='store', dest='localstart',help='Start A Stopped Container')
parser.add_argument('-r', action='store', dest='localremove',help='Remove A Stopped Container')
parser.add_argument('-rmf', action='store', dest='localforceremove',help='Force Remove A Running Container')
parser.add_argument('-b1', action='store', dest='localbash',help='Bash Into A Running Container')
parser.add_argument('-b2', action='store', dest='localsh',help='Sh Into A Running Container')
parser.add_argument('-rmi', action='store', dest='localremoveimage',help='Remove An Image')
parser.add_argument('-rmif', action='store', dest='localforceremoveimage',help='Force Remove An Image')
parser.add_argument('-local', action='store', dest='locallocal',help='Toggle Local Server Support')
parser.add_argument('-remote', action='store', dest='localremote',help='Toggle Remote Server Support')
parser.add_argument('-ip', action='store', dest='localip',help='Remote IP Address')
parser.add_argument('-user', action='store', dest='localuser',help='Remote Username')
parser.add_argument('-passwd', action='store', dest='localpasswd',help='Remote Password')

if(len(sys.argv) >= 2):
    if(sys.argv[1] == '-s'):   
        cmd = DOCKER_PATH + " stop " + sys.argv[2]
        run_script(cmd)
        sys.exit(0)     

    elif(sys.argv[1] == '-t'):   
        cmd = DOCKER_PATH + " start " + sys.argv[2]
        run_script(cmd)
        sys.exit(0)    
    
    elif(sys.argv[1] == '-r'):   
        cmd = DOCKER_PATH + " rm " + sys.argv[2]
        run_script(cmd)
        sys.exit(0)    

    elif(sys.argv[1] == '-rmf'):   
        cmd = DOCKER_PATH + " rm -f " + sys.argv[2]
        #print cmd
        run_script(cmd)
        sys.exit(0)  

    elif(sys.argv[1] == '-b1'):
        cmd = DOCKER_PATH + " exec -it " + sys.argv[2] + " /bin/bash"
        #print cmd
        os.system('echo "Running: {}";{}'.format(cmd,cmd))
        sys.exit(0)     

    elif(sys.argv[1] =='-b2'):
        cmd = DOCKER_PATH + " exec -it " + sys.argv[2] + " /bin/sh"
        #print cmd
        os.system('echo "Running: {}";{}'.format(cmd,cmd))
        sys.exit(0)       

    elif(sys.argv[1] == '-rmi'):   
        cmd = DOCKER_PATH + " rmi " + sys.argv[2]
        run_script(cmd)
        #print cmd
        sys.exit(0)  

    elif(sys.argv[1] == '-rmif'):   
        cmd = DOCKER_PATH + " rmi -f " + sys.argv[2]
        #print cmd
        run_script(cmd)
        sys.exit(0)  

    elif(sys.argv[1] == '-local'):   
        local_enabled = not local_enabled
        with open(local_path, 'w') as f:
            if local_enabled:
                f.write('True')
            else:
                f.write('False')
        sys.exit(0)

    elif(sys.argv[1] == '-remote'):   
        remote_enabled = not remote_enabled
        with open(remote_path, 'w') as f:
            if remote_enabled:
                f.write('True')
            else:
                f.write('False')
        sys.exit(0)
            
    elif(sys.argv[1] == '-ip'):   
        cmd = "osascript -e \'set theString to text returned of (display dialog \"Please Enter The IP Address Of Your Remote Server. \n\nIt will be stored in:\n{}".format(ip_path) + "  \" with icon note default answer \"\" buttons {\"OK\",\"Cancel\"} default button 1) \'" 
        ip = run_script(cmd)
        with open(ip_path, 'w') as f:
            f.write(ip)
        sys.exit(1)

    elif(sys.argv[1] == '-user'):   
        cmd = "osascript -e \'set theString to text returned of (display dialog \"Please Enter Username On Your Remote Server. \n\nIt will be stored in:\n{}".format(user_path) + "  \" with icon note default answer \"\" buttons {\"OK\",\"Cancel\"} default button 1) \'" 
        user = run_script(cmd)
        with open(user_path, 'w') as f:
            f.write(user)
        sys.exit(1)

    elif(sys.argv[1] == '-passwd'):   
        cmd = "osascript -e \'set theString to text returned of (display dialog \"Please Enter The Password For Your Remote Server. \n\nIt will be stored in:\n{}".format(passwd_path) + "  \" with icon note default answer \"\" buttons {\"OK\",\"Cancel\"} default button 1) \'" 
        passwd = run_script(cmd)
        with open(passwd_path, 'w') as f:
            f.write(passwd)
        sys.exit(1)
     

#print '🐳'
print '| image={}'.format(moby_icon)
print '---'
if local_enabled:
    print "🏠 Local Docker |  color=#30C102 bash=" + ME_PATH +  " param1=-local param2=null terminal=false refresh=true" 
    print '---'
    #-----------------------------------------------------------------------------------------------------------
    # Get Local Docker Containers
    #-----------------------------------------------------------------------------------------------------------
    cmd_output=run_script(DOCKERPS_CMD)
    print_containers(cmd_output, local=True, size=10)  

    #-----------------------------------------------------------------------------------------------------------
    # Get Local Docker Images
    #-----------------------------------------------------------------------------------------------------------
    cmd_output = run_script(DOCKERIMAGES_CMD)
    print_images(cmd_output, local=True, size=10)

    #-----------------------------------------------------------------------------------------------------------
    # Get Local Docker Info
    #-----------------------------------------------------------------------------------------------------------
    dockerinfo_output=run_script(DOCKER_PATH + ' info')
    print_info(dockerinfo_output, local=True, size=10)

    #-----------------------------------------------------------------------------------------------------------
    # Get Local Docker Daemon (if any)
    #-----------------------------------------------------------------------------------------------------------
    daemoninfo = ''
    if os.path.isfile(LOCAL_DAEMON_PATH) :
        with open(LOCAL_DAEMON_PATH, 'r') as file:
            daemoninfo = file.read()
    print_daemon(daemoninfo, local=True, size=10)
    
else:
    print "🏠 Local Docker | color=gray bash=" + ME_PATH +  " param1=-local param2=null terminal=false refresh=true"
print '---'

#-----------------------------------------------------------------------------------------------------------
# 
#-----------------------------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------------------------
# Remote Docker Check/Config
#-----------------------------------------------------------------------------------------------------------
#remote_enabled=False
if remote_enabled:
    print "☁️ Remote Docker | color=#30C102  bash=" + ME_PATH +  " param1=-remote param2=null terminal=false refresh=true" + c.ENDC
else:
    print "☁️ Remote Docker | color=gray bash=" + ME_PATH +  " param1=-remote param2=null terminal=false refresh=true" + c.ENDC
    print_refresh()
    sys.exit(0)

print '-- Set IP |  bash=' + ME_PATH +  ' param1=-ip param2=null terminal=false refresh=true'
print '----', ip
print '-- Set username |  bash=' + ME_PATH +  ' param1=-user param2=null terminal=false refresh=true'
print '----', user
print '-- Set password |  bash=' + ME_PATH +  ' param1=-passwd param2=null terminal=false refresh=true'
print '----', passwd

if '' in (ip, user, passwd):
    print_refresh() 
    sys.exit(0)

#-----------------------------------------------------------------------------------------------------------
# Remote Docker
#-----------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------
# SSH To Remote Server
#-----------------------------------------------------------------------------------------------------------
SSH_CMD = 'ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no {}'.format(user)
command = SSH_CMD+'@{}'.format(ip)
#logger.info('SSH to device.')
#logger.info('SSH command is: ' + c.CYAN + c.UNDERLINE + '{}'.format(command) + c.ENDC)
child = pexpect.spawn (command)
child.logfile_read = None  #Set to logger to see the child output
child.logfile_send = None  #Set to None to hide password

i = child.expect([pexpect.TIMEOUT, '.*assword:', '.*refused', pexpect.EOF])
#logger.debug('i is: {}'.format(i))
if i != 1:
    #die(child, 'ERROR! SSH Failed:', ip)
    exit(0)
child.delaybeforesend = 1
child.sendline(passwd)
child.sendline('')

i = child.expect([pexpect.TIMEOUT, 'Permission denied', 'closed by remote host', '{}'.format(LOCAL_PROMPT), pexpect.EOF])
#logger.debug('i is: {}'.format(i))
if i == 0:
    #die(child, 'ERROR! SSH timed out:', ip)
    exit(0)
elif i == 1:
    #die(child, 'ERROR! Incorrect password:', ip)
    exit(0)
elif i == 2:
    #die(child, 'ERROR! Connection Closed:', ip)
    exit(0)
result = child.before.decode('utf-8', 'ignore')
#logger.info(result)

print "---"
#-----------------------------------------------------------------------------------------------------------
# Get Remote Docker Containers
#-----------------------------------------------------------------------------------------------------------
cmd_output = run_remote_cmd(DOCKERPS_CMD, child)
print_containers(cmd_output, local=False, size=10, sess=child)  

#-----------------------------------------------------------------------------------------------------------
# Get Remote Docker Images
#-----------------------------------------------------------------------------------------------------------
cmd_output = run_remote_cmd(DOCKERIMAGES_CMD, child)
print_images(cmd_output, local=False, size=10)

#-----------------------------------------------------------------------------------------------------------
# Get Remote Docker Info
#-----------------------------------------------------------------------------------------------------------
daemon_output=run_remote_cmd(DOCKER_PATH + ' info' , child)
print_info(daemon_output, local=False, size=11)

#-----------------------------------------------------------------------------------------------------------
# Get Remote Docker Daemon (if any)
#-----------------------------------------------------------------------------------------------------------
daemoninfo = ''
daemon_output=run_remote_cmd('cat '+REMOTE_DAEMON_PATH, child)
print_daemon(daemon_output, local=False)

child.close()
print_refresh()