"""Authentication tools for Warbler"""

from functools import wraps
from flask import redirect, session, flash, abort


def requires_auth(username=''):
  '''Takes username from URL and checks if user is logged in'''

  def requires_auth_decorator(f):
      @wraps(f)
      def wrapper(username, *args, **kwargs):

        current_user = session.get('username', None)

        if username != current_user:
            if current_user:
                flash('Access unauthorized.', category='danger')
                return redirect('/')
                # abort(401)
            flash('Access unauthorized.', category='danger')
            return redirect('/')
            # abort(401)
            
        return f(username, *args, **kwargs)

      return wrapper
  return requires_auth_decorator

def requires_signed_in(f):
    """Decorator restricting route to logged in users"""
    
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'curr_user' not in session:
            flash('Access unauthorized.', category='danger')
            return redirect('/')
            # abort(401)
        return f(*args, **kwargs)

    return decorated


def requires_signed_out(f):
    """Decorator restricting route to users not logged in"""
    
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'username' in session:
            flash('You are already logged in!', category='warning')
            username = session.get('username')
            return redirect(f'/users/{username}')
        return f(*args, **kwargs)

    return decorated