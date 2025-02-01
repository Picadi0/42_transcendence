import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
import logging
from .models import GameDB
from .models import TMPGameDB
from datetime import datetime
from asgiref.sync import sync_to_async

logger = logging.getLogger(__name__)


class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        logger.error("Websocket bağlaniyor")
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.user_id = self.scope["url_route"]["kwargs"]["user_id"]
        self.group_name = self.room_id

        # Kullaniciyi channel gruba ekle
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        userCanJoinRoom = False
        self.startGame = False
        sendStartBroadCast = False
        try:
            # Fetch all rooms and evaluate the QuerySet synchronously
            rooms = await sync_to_async(list)(TMPGameDB.objects.all())

            # Check if user is in any room (player1 or player2) using in-memory list
            for room in rooms:
                if room.room_id == self.room_id:
                    if room.player1_id == self.user_id:
                        self.isHost = True
                        userCanJoinRoom = True
                    elif room.player2_id == self.user_id:
                        self.isHost = False
                        userCanJoinRoom = True
                    else:
                        userCanJoinRoom = False
                    if room.player1_id and room.player2_id:
                        sendStartBroadCast = True
                    break

        except Exception as e:
            logger.error(f"game/Consumer.py Error {e}")
            await self.close()
            return

        if userCanJoinRoom:
            await self.accept()
            asyncio.create_task(self.update())
            self.isConnected = True
            logger.error(f"{self.user_id} şu oyuna {self.room_id} katildi")
            logger.error(f"Herkes hazir mi status {sendStartBroadCast}")
        else:
            logger.error(
                f"error: {self.user_id} şu oyuna {self.room_id} katilamadi çünkü gameDb'de bulunamadi"
            )
            await self.close()


    async def update(self):
        while self.isConnected:
            if self.startGame == False:
                logger.error("Update Calisiyor")
                rooms = await sync_to_async(list)(TMPGameDB.objects.all())
                for room in rooms:
                    if room.room_id == self.room_id:
                        if room.player1_id and room.player2_id:
                            self.startGame = True
                await asyncio.sleep(1)
            else:
                self.update_ball()
                await asyncio.sleep(0.016)#60 fpsmişmiş

    async def update_ball(self):
        return

    # Kullaniciyi gruptan çikar
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        self.isConnected = False
        await self.endOfGame()
        

    # Gruptan gelen mesaji kullaniciya ilet
    async def receive(self, text_data):
        logger.error("receive cagrildi")
        try:
            text_data_json = json.loads(text_data)
            if not hasattr(self, "p1_y"):
                self.p1_y = 50
            if not hasattr(self, "p2_y"):
                self.p2_y = 50
            if "type" not in text_data_json:
                await self.send(
                    json.dumps(
                        {
                            "status": "error",
                            "message": "There must be type key as json format",
                        }
                    )
                )
            else:
                type = text_data_json["type"]
                if type == "ping":
                    await self.send(
                        json.dumps(
                            {
                                "status": "success",
                                "message": "pong",
                            }
                        )
                    )
                elif type == "move" and self.startGame:
                    direction = text_data_json["direction"]
                    if direction == "up":
                        if self.isHost and self.p1_y > 0 and self.p1_y <= 100:
                            self.p1_y -= 2
                            await self.send_msg({"type": "move", "p1_y": self.p1_y, "user_id": self.user_id})
                        elif not self.isHost and self.p2_y > 0 and self.p2_y <= 100:
                            self.p2_y -= 2
                            await self.send_msg({"type": "move", "p2_y": self.p2_y, "user_id": self.user_id})
                    elif direction == "down":
                        if self.isHost and self.p1_y >= 0 and self.p1_y < 100:
                            self.p1_y += 2
                            await self.send_msg({"type": "move", "p1_y": self.p1_y, "user_id": self.user_id})
                        elif not self.isHost and self.p2_y >= 0 and self.p2_y < 100:
                            self.p2_y += 2
                            await self.send_msg({"type": "move", "p2_y": self.p2_y, "user_id": self.user_id})
                    if self.isHost:
                        logger.error(f"p1_y ={self.p1_y}")
                    else:
                        logger.error(f"p2_y ={self.p2_y}")
        except Exception as e:
            logger.error(f"receive Error :{e}")

    # Mesaji gruba gönder
    async def send_msg(self, jsonmsg):
        await self.channel_layer.group_send(
            self.group_name, {"type": "group_message", "jsonmsg": jsonmsg}
        )

    # Grup mesajini işle
    async def group_message(self, event):
        jsonmsg = event["jsonmsg"]

        # Mesaji WebSocket üzerinden gönder
        await self.send(json.dumps(jsonmsg))

    async def endOfGame(self):
        try:
            # Use sync_to_async to run synchronous database queries
            room = await sync_to_async(
                TMPGameDB.objects.filter(room_id=self.room_id).first
            )()

            if room:
                # Determine the remaining player
                if self.user_id == room.player1_id:
                    remaining_player_id = room.player2_id
                elif self.user_id == room.player2_id:
                    remaining_player_id = room.player1_id
                else:
                    logger.error(f"Kullanici {self.user_id} bu odada bulunamadi.")
                    return

                # If there's a remaining player, mark them as the winner
                if remaining_player_id:
                    # Update TMPGameDB
                    room.winner_id = remaining_player_id
                    room.end_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    await sync_to_async(room.save)()

                    # Create a new record in GameDB
                    await sync_to_async(GameDB.objects.create)(
                        room_id=room.room_id,
                        player1_id=room.player1_id,
                        player1_score=room.player1_score,
                        player2_id=room.player2_id,
                        player2_score=room.player2_score,
                        winner_id=remaining_player_id,
                        create_date=room.create_date,
                        end_date=room.end_date,
                    )
                    logger.error(f"{self.user_id} Oyun verileri kayit edildi.")
                    # Delete the room from TMPGameDB
                    logger.error(f"{room.room_id} oda silindi.")
                    await sync_to_async(room.delete)()
                    logger.error(
                        f"Kullanici {self.user_id} odadan ayrildi. Kazanan: {remaining_player_id}"
                    )
                    await self.send_msg({"type": "disconnect", "Winner": remaining_player_id})
                else:
                    logger.error(
                        f"Kullanici {self.user_id} odadan ayrildi, Kazanan olmadi çünkü rakip yoktu."
                    )
                    logger.error(f"{room.room_id} oda silindi.")
                    await sync_to_async(room.delete)()
            else:
                logger.error(f"Websocket disconnect olurken {self.room_id} bulunamadi")
        except Exception as e:
            logger.error(f"endOfGame metodunda hata: {e}")