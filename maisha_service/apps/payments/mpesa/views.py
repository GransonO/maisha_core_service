# Create your views here.
import bugsnag
from rest_framework import views,  status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import MpesaEntryDB


class MpesaCallback(views.APIView):
    """
        Pick all MPESA details and save in DB
    """
    permission_classes = [AllowAny]

    @staticmethod
    def post(request):
        """ Reassign Tier groups to members """
        passed_data = request.data
        print("The passed_data is -------------: {}".format(passed_data))

        body = passed_data['Body']
        callback_body = body['stkCallback']
        merchant_request_id = callback_body['MerchantRequestID']
        result_code = callback_body['ResultCode']
        result_desc = callback_body['ResultDesc']
        callback_metadata = callback_body['CallbackMetadata']

        item = callback_metadata['Item']
        if len(item) < 5:
            amount = item[0]['Value']
            mpesa_receipt_number = item[1]['Value']
            transaction_date = item[2]['Value']
            phone_number = item[3]['Value']
        else:
            amount = item[0]['Value']
            mpesa_receipt_number = item[1]['Value']
            transaction_date = item[3]['Value']
            phone_number = item[4]['Value']

        mpesa_data = MpesaEntryDB(
            MerchantRequestID=merchant_request_id,
            ResultCode=result_code,
            ResultDesc=result_desc,
            Amount=amount,
            MpesaReceiptNumber=mpesa_receipt_number,
            TransactionDate=transaction_date,
            Client_phone=phone_number
        )
        mpesa_data.save()
        return Response({"DONE"}, status.HTTP_200_OK)

    @staticmethod
    def put(request):
        """Get the Mpesa value deposited"""
        passed_data = request.data
        trans_num = passed_data["MerchantRequestID"]
        try:
            result = MpesaEntryDB.objects.get(
                MerchantRequestID=trans_num)
            print("The response is : {}".format(result))
            return Response({
                    "status": "success",
                    "code": 1,
                    "customer_phone": result.Client_phone,
                    "receipt_number": result.MpesaReceiptNumber,
                    "amount": result.Amount,
                }, status.HTTP_200_OK)

        except Exception as E:
            print("Error: {}".format(E))
            bugsnag.notify(
                Exception('Transaction Put: {}'.format(E))
            )
            return Response({
                "error": "{}".format(E),
                "status": "failed",
                "code": 0
                }, status.HTTP_200_OK)
