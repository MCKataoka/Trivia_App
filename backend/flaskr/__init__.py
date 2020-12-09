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

    @app.route('/categories/<int:question_id>/questions')
    def get_questions_by_category(question_id):
        selection = Question.query.order_by(
            Question.id).filter(Question.category == question_id).all()

        current_questions = paginate_questions(request, selection)
        if len(current_questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(selection),
            'current_category': question_id
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
            print('NEW QUESTIONS, ', new_question)
            print('ANSWER, ', new_answer)
            print('DIFFICULTY, ', new_difficulty)
            print('CATEGORY, ', new_category)
            question = Question(question=new_question, answer=new_answer,
                                difficulty=str(new_difficulty), category=int(new_category))

            print('QUESTION, ', question)
            question.insert()

            selection = Question.query.order_by(Book.id).all()
            current_questions = paginate_books(request, selection)

            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': len(Question.query.all()),
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

    return app

  #   '''
  # @TODO:
  # Create an endpoint to handle GET requests
  # for all available categories.
  # '''

  #   '''
  # @TODO:
  # Create an endpoint to POST a new question,
  # which will require the question and answer text,
  # category, and difficulty score.

  # TEST: When you submit a question on the "Add" tab,
  # the form will clear and the question will appear at the end of the last page
  # of the questions list in the "List" tab.
  # '''

  #   '''
  # @TODO:
  # Create a POST endpoint to get questions based on a search term.
  # It should return any questions for whom the search term
  # is a substring of the question.

  # TEST: Search by any phrase. The questions list will update to include
  # only question that include that string within their question.
  # Try using the word "title" to start.
  # '''

  #   '''
  # @TODO:
  # Create a GET endpoint to get questions based on category.

  # TEST: In the "List" tab / main screen, clicking on one of the
  # categories in the left column will cause only questions of that
  # category to be shown.
  # '''

  #   '''
  # @TODO:
  # Create a POST endpoint to get questions to play the quiz.
  # This endpoint should take category and previous question parameters
  # and return a random questions within the given category,
  # if provided, and that is not one of the previous questions.

  # TEST: In the "Play" tab, after a user selects "All" or a category,
  # one question at a time is displayed, the user is allowed to answer
  # and shown whether they were correct or not.
  # '''

  #   '''
  # @TODO:
  # Create error handlers for all expected errors
  # including 404 and 422.
  # '''
