import bugsnag
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
import json

from maisha_service.apps.core.models import MaishaCore, SessionBounce
from maisha_service.apps.core.serializers import MaishaCoreSerializer, SessionBounceSerializer
from maisha_service.apps.profiles.models import DoctorsProfiles


class SocketCore(AsyncWebsocketConsumer):
    async def connect(self):
        # Join room group
        await self.channel_layer.group_add(
            "MAISHA_CORE_SERVICE",
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            "MAISHA_CORE_SERVICE",
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        core_request = text_data_json["core_request"]

        if text_data_json["request_type"] == "REQUESTING":
            # patient sending out sequential requests
            core_response = await self.post_core_request(core_request)

            # Send message to room group
            if core_response["success"]:
                # Notifying doctors if request is success
                await self.channel_layer.group_send(
                    "MAISHA_CORE_SERVICE",
                    {
                        'type': 'core_request',
                        'profile': 'DOCTOR',
                        'status': 'OPEN',  # If request is still active
                        'user_id': core_request['doctor_id'],
                        'data': core_request,
                        'success': True
                    }
                )
            else:
                # Notify patient of request failure
                await self.channel_layer.group_send(
                    "MAISHA_CORE_SERVICE",
                    {
                        'profile': 'PATIENT',
                        'status': 'CLOSED',
                        'user_id': core_request['patient_id'],
                        'session_id': core_request['session_id'],
                        'message': core_response["message"],
                        'type': 'core_request',
                        'success': False
                    }
                )
        else:
            # Doctor Responding to patient
            core_response = await self.update_core_request(core_request)

            # Send message to room group
            if core_response["success"]:
                # Notify patient if of the update
                await self.channel_layer.group_send(
                    "MAISHA_CORE_SERVICE",
                    {
                        'profile': 'PATIENT',
                        'type': 'core_request',
                        'user_id': core_request['patient_id'],
                        'session_id': core_request['session_id'],
                        'doctor_id': core_request['doctor_id'],
                        'status': core_request['status'],
                        'success': True
                    }
                )
            else:
                # Notify doctor of request failure
                await self.channel_layer.group_send(
                    "MAISHA_CORE_SERVICE",
                    {
                        'profile': 'DOCTOR',
                        'user_id': core_request['doctor_id'],
                        'session_id': core_request['session_id'],
                        'message': core_response["message"],
                        'type': 'core_request',
                        'success': False
                    }
                )

    # Receive message from room group
    async def core_request(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def post_core_request(self, passed_data):
        # Patient resend request to next doctor
        try:
            # Save the request
            session = MaishaCore.objects.get(session_id=passed_data["session_id"])
            serialized_session = MaishaCoreSerializer(session).data

            if serialized_session["status"] == "ACCEPTED":
                # Accepted or Cancelled
                response = {
                        "success": False,
                        "message": "Request already taken"
                    }

                return response
            else:
                serializer = SessionBounceSerializer(data=passed_data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                # FcmCore.doctor_core_notice(
                #     all_tokens=[passed_data["doctor_fcm"]],
                #     message="Maisha {} request".format(passed_data["type"]),
                #     description=passed_data["description"],
                #     user_id=passed_data["patient_id"],
                #     patient_fcm=passed_data["patient_fcm"],
                #     session_id=passed_data["session_id"],
                #     type=passed_data["type"]
                # )

                response = {
                    "success": True,
                    "message": "Posted successfully"
                }
                return response

        except Exception as E:
            bugsnag.notify(
                Exception('CoreRequest Post: {}'.format(E))
            )
            response = {
                    "success": False,
                    "message": "Posting failed"
                }
            return response

    @database_sync_to_async
    def update_core_request(self, passed_data):
        try:
            session = MaishaCore.objects.get(session_id=passed_data["session_id"])
            session_details = MaishaCoreSerializer(session).data

            if session_details["status"] == "ACCEPTED":
                return {
                    "success": False,
                    "message": "Request already taken"
                }

            serializer = MaishaCoreSerializer(
                session, data=passed_data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

            # Debounce Updater
            debounce_session = SessionBounce.objects.filter(
                session_id=passed_data["session_id"], doctor_id=passed_data["doctor_id"])
            debounce_session.update(doc_response=passed_data["status"])

            if passed_data["status"] == "ACCEPTED":
                # take Accepting doctor offline
                DoctorsProfiles.objects.filter(user_id=passed_data["doctor_id"]).update(is_online=False)
                # Sent only if Doc Accepts the request
                # FcmCore.patient_core_notice(
                #     all_tokens=[passed_data["patient_fcm"]],
                #     message="Maisha request update",
                #     doctor_id=passed_data["doctor_id"],
                #     session_id=passed_data["session_id"],
                #     status=passed_data["status"],
                # )

                return {
                    "success": True,
                    "message": "Posted successfully"
                }

        except Exception as E:
            print("---E--------------------{}".format(E))
            bugsnag.notify(
                Exception('CoreRequest Post: {}'.format(E))
            )
            return {
                    "success": False,
                    "message": "Posting failed"
                }
