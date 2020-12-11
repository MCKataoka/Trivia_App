import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    def paginate_questions(request, selection):
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        questions = [question.format() for question in selection]
        current_questions = questions[start:end]

        return current_questions

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PUT,POST,DELETE,OPTIONS,PATCH')
        return response

    @app.route('/questions')
    def get_questions():
        selection = Question.query.order_by(Question.id).all()
        categories = Category.query.order_by(Category.id).all()

        # category = [dict() for x in range(len(categories))]

        category = {}

        for i, cat in enumerate(categories):
            category[categories[i].id] = categories[i].type

        current_quiestions = paginate_questions(request, selection)
        if len(current_quiestions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': current_quiestions,
            'total_questions': len(Question.query.all()),
            'categories': category
        })

    @app.route('/categories')
    def get_categories():

        categories = Category.query.order_by(Category.id).all()
        category = {}

        for i, cat in enumerate(categories):
            category[categories[i].id] = categories[i].type

        return jsonify({
            'success': True,
            'categories': category
        })

    @app.route('/categories/<int:category_id>/questions')
    def get_questions_by_category(category_id):
        selection = Question.query.order_by(
            Question.id).filter(Question.category == category_id).all()

        current_questions = paginate_questions(request, selection)
        if len(current_questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(selection),
            'current_category': category_id
        })

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.filter(
                Question.id == question_id).one_or_none()
            if question is None:
                abort(404)

            question.delete()

            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            return jsonify({
                'success': True,
                'deleted': question_id,
                'questions': current_questions,
                'total_questions': len(Question.query.all())
            })
        except:
            abort(422)

    @app.route('/questions', methods=['POST'])
    def add_question():
        body = request.get_json()

        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_difficulty = body.get('difficulty', None)
        new_category = body.get('category', None)

        try:

            question = Question(question=new_question, answer=new_answer,
                                difficulty=str(new_difficulty), category=int(new_category))

            question.insert()

            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': len(Question.query.all()),
            })
        except:
            abort(422)

    @app.route('/questions/search', methods=['POST'])
    def search_question():
        body = request.get_json()

        searchTerm = body.get('searchTerm', None)

        try:
            selection = Question.query.order_by(Question.id).filter(
                Question.question.ilike('%{}%'.format(searchTerm)))
            current_questions = paginate_questions(request, selection)

            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': len(selection.all())
            })
        except:
            abort(422)

    @ app.route('/quizzes', methods=['POST'])
    def make_quiz():
        body = request.get_json()

        previous_questions = body.get('previous_questions', None)
        quiz_category = body.get('quiz_category', None)

        try:

            if(quiz_category['id'] == 0):
                quiz_questions = Question.query.all()
            else:
                quiz_questions = Question.query.filter(
                    Question.category == quiz_category['id']).all()

            possible_questions = []
            for question in quiz_questions:
                if question.id not in previous_questions:
                    possible_questions.append(question.format())

            if len(possible_questions) != 0:
                final_q = random.choice(possible_questions)
                return jsonify({
                    'success': True,
                    'question': final_q
                })
            else:
                return jsonify({
                    'success': True,
                    'question': False
                })

        except:
            abort(422)

    @ app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @ app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @ app.errorhandler(500)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "Internal Server Error"
        }), 500

    @ app.errorhandler(400)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad Request Error"
        }), 400

    @ app.errorhandler(405)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "method not allowed"
        }), 405

    return app
