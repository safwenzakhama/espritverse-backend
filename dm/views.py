from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from django.db.models import Q, Max
from django.contrib.auth import get_user_model

from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer, CreateConversationSerializer

User = get_user_model()


class ConversationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing conversations"""
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (JSONParser, FormParser, MultiPartParser)

    def get_queryset(self):
        """Return conversations where the current user is a participant"""
        return Conversation.objects.filter(
            participants=self.request.user
        ).annotate(
            last_message_time=Max('messages__created_at')
        ).order_by('-last_message_time', '-updated_at')

    def perform_create(self, serializer):
        """Add current user as participant when creating conversation"""
        conversation = serializer.save()
        conversation.participants.add(self.request.user)

    @action(detail=False, methods=['post'])
    def open(self, request):
        """Open or create a conversation with another user"""
        serializer = CreateConversationSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user_id = serializer.validated_data['user_id']
            other_user = User.objects.get(id=user_id)
            
            # Check if conversation already exists
            conversation = Conversation.objects.filter(
                participants=request.user
            ).filter(
                participants=other_user
            ).distinct().first()
            
            if not conversation:
                # Create new conversation
                conversation = Conversation.objects.create()
                conversation.participants.add(request.user, other_user)
            
            serializer = ConversationSerializer(conversation, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MessageViewSet(viewsets.ModelViewSet):
    """ViewSet for managing messages"""
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (JSONParser, FormParser, MultiPartParser)

    def get_queryset(self):
        """Return messages for conversations where the current user is a participant"""
        conversation_id = self.request.query_params.get('conversation')
        if conversation_id:
            # Check if user is participant in this conversation
            try:
                conversation = Conversation.objects.get(
                    id=conversation_id,
                    participants=self.request.user
                )
                return Message.objects.filter(conversation=conversation)
            except Conversation.DoesNotExist:
                return Message.objects.none()
        return Message.objects.none()

    def create(self, request, *args, **kwargs):
        """Override create to add better error handling"""
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as e:
            print(f"Message creation error: {str(e)}")
            print(f"Request data: {request.data}")
            print(f"Request files: {request.FILES}")
            return Response(
                {'error': str(e), 'details': 'Failed to create message'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    def perform_create(self, serializer):
        """Set sender to current user when creating message"""
        serializer.save(sender=self.request.user)

    @action(detail=True, methods=['patch'])
    def mark_read(self, request, pk=None):
        """Mark a message as read"""
        message = self.get_object()
        message.is_read = True
        message.save()
        return Response({'status': 'message marked as read'})

    @action(detail=False, methods=['post'])
    def mark_conversation_read(self, request):
        """Mark all messages in a conversation as read"""
        conversation_id = request.data.get('conversation_id')
        if not conversation_id:
            return Response({'error': 'conversation_id required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            conversation = Conversation.objects.get(
                id=conversation_id,
                participants=request.user
            )
            Message.objects.filter(
                conversation=conversation
            ).exclude(
                sender=request.user
            ).update(is_read=True)
            
            return Response({'status': 'conversation marked as read'})
        except Conversation.DoesNotExist:
            return Response({'error': 'Conversation not found'}, status=status.HTTP_404_NOT_FOUND)
