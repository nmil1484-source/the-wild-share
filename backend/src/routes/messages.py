from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import db, User
from src.models.equipment import Equipment
from src.models.message import Message
from src.utils.email_notifications import send_new_message_notification_email

messages_bp = Blueprint('messages', __name__)

@messages_bp.route('/equipment/<int:equipment_id>/messages', methods=['POST'])
@jwt_required()
def send_message(equipment_id):
    """Send a message about an equipment item"""
    sender_id = int(get_jwt_identity())
    data = request.get_json()
    
    if 'message' not in data:
        return jsonify({'error': 'Message is required'}), 400
    
    # Get equipment and owner
    equipment = Equipment.query.get(equipment_id)
    if not equipment:
        return jsonify({'error': 'Equipment not found'}), 404
    
    # Determine receiver (if sender is owner, can't message themselves)
    if sender_id == equipment.owner_id:
        return jsonify({'error': 'Cannot send message to yourself'}), 400
    
    receiver_id = equipment.owner_id
    
    # Create message
    new_message = Message(
        equipment_id=equipment_id,
        sender_id=sender_id,
        receiver_id=receiver_id,
        message=data['message']
    )
    
    db.session.add(new_message)
    db.session.commit()
    
    # Send email notification to receiver
    try:
        sender = User.query.get(sender_id)
        receiver = User.query.get(receiver_id)
        send_new_message_notification_email(new_message, sender, receiver, equipment)
    except Exception as e:
        print(f"Error sending message notification email: {e}")
    
    return jsonify({
        'message': 'Message sent successfully',
        'data': new_message.to_dict()
    }), 201

@messages_bp.route('/equipment/<int:equipment_id>/messages', methods=['GET'])
@jwt_required()
def get_equipment_messages(equipment_id):
    """Get all messages for an equipment item (for owner and interested renters)"""
    user_id = int(get_jwt_identity())
    
    # Get equipment
    equipment = Equipment.query.get(equipment_id)
    if not equipment:
        return jsonify({'error': 'Equipment not found'}), 404
    
    # Get messages where user is sender or receiver
    messages = Message.query.filter(
        Message.equipment_id == equipment_id,
        db.or_(
            Message.sender_id == user_id,
            Message.receiver_id == user_id
        )
    ).order_by(Message.created_at.asc()).all()
    
    # Mark received messages as read
    for msg in messages:
        if msg.receiver_id == user_id and not msg.is_read:
            msg.is_read = True
    
    db.session.commit()
    
    return jsonify([msg.to_dict() for msg in messages]), 200

@messages_bp.route('/messages', methods=['GET'])
@jwt_required()
def get_my_messages():
    """Get all message conversations for current user"""
    user_id = int(get_jwt_identity())
    
    # Get all messages where user is sender or receiver
    messages = Message.query.filter(
        db.or_(
            Message.sender_id == user_id,
            Message.receiver_id == user_id
        )
    ).order_by(Message.created_at.desc()).all()
    
    # Group by equipment and conversation partner
    conversations = {}
    for msg in messages:
        equipment_id = msg.equipment_id
        partner_id = msg.sender_id if msg.receiver_id == user_id else msg.receiver_id
        
        key = f"{equipment_id}_{partner_id}"
        
        if key not in conversations:
            conversations[key] = {
                'equipment_id': equipment_id,
                'equipment_name': msg.equipment.name if msg.equipment else None,
                'partner_id': partner_id,
                'partner_name': f"{msg.sender.first_name} {msg.sender.last_name}" if msg.receiver_id == user_id else f"{msg.receiver.first_name} {msg.receiver.last_name}",
                'last_message': msg.message,
                'last_message_time': msg.created_at.isoformat() if msg.created_at else None,
                'unread_count': 0
            }
        
        # Count unread messages
        if msg.receiver_id == user_id and not msg.is_read:
            conversations[key]['unread_count'] += 1
    
    return jsonify(list(conversations.values())), 200

@messages_bp.route('/messages/unread-count', methods=['GET'])
@jwt_required()
def get_unread_count():
    """Get count of unread messages"""
    user_id = int(get_jwt_identity())
    
    unread_count = Message.query.filter_by(
        receiver_id=user_id,
        is_read=False
    ).count()
    
    return jsonify({'unread_count': unread_count}), 200

@messages_bp.route('/messages/<int:message_id>/read', methods=['PUT'])
@jwt_required()
def mark_message_read(message_id):
    """Mark a message as read"""
    user_id = int(get_jwt_identity())
    
    message = Message.query.get(message_id)
    if not message:
        return jsonify({'error': 'Message not found'}), 404
    
    if message.receiver_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    message.is_read = True
    db.session.commit()
    
    return jsonify({'message': 'Message marked as read'}), 200

