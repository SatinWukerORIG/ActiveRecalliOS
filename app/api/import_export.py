"""
Import/Export API endpoints
"""
from flask import request, jsonify, make_response
from app.api import api_bp
from app.models import User
from app.utils.data_import import DataImporter

@api_bp.route('/users/<int:user_id>/import/csv', methods=['POST'])
def import_csv(user_id):
    """Import cards from CSV data"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    data = request.json
    if not data or 'csv_content' not in data:
        return jsonify({"error": "CSV content is required"}), 400
    
    csv_content = data['csv_content']
    delimiter = data.get('delimiter', ',')
    
    result = DataImporter.import_from_csv(user_id, csv_content, delimiter)
    
    if result['success']:
        return jsonify({
            "message": f"Successfully imported {result['imported_count']} cards",
            "imported_count": result['imported_count'],
            "errors": result['errors']
        }), 201
    else:
        return jsonify({
            "error": result['error'],
            "imported_count": result['imported_count'],
            "errors": result['errors']
        }), 400

@api_bp.route('/users/<int:user_id>/import/anki', methods=['POST'])
def import_anki(user_id):
    """Import cards from Anki JSON export"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    data = request.json
    if not data or 'json_content' not in data:
        return jsonify({"error": "JSON content is required"}), 400
    
    json_content = data['json_content']
    
    result = DataImporter.import_from_anki_json(user_id, json_content)
    
    if result['success']:
        return jsonify({
            "message": f"Successfully imported {result['imported_count']} cards from Anki",
            "imported_count": result['imported_count'],
            "errors": result['errors']
        }), 201
    else:
        return jsonify({
            "error": result['error'],
            "imported_count": result['imported_count'],
            "errors": result['errors']
        }), 400

@api_bp.route('/users/<int:user_id>/export/csv', methods=['GET'])
def export_csv(user_id):
    """Export user's cards to CSV"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    try:
        csv_content = DataImporter.export_to_csv(user_id)
        
        response = make_response(csv_content)
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename=active_recall_cards_{user.username}.csv'
        
        return response
        
    except Exception as e:
        return jsonify({"error": f"Failed to export cards: {str(e)}"}), 500

@api_bp.route('/import/template', methods=['GET'])
def get_import_template():
    """Get CSV template for importing cards"""
    template = DataImporter.get_import_template()
    
    response = make_response(template)
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = 'attachment; filename=active_recall_import_template.csv'
    
    return response