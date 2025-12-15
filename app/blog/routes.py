"""
Blog Routes
Blog post management
"""
from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from app.models import Post, User
from app.utils.decorators import login_required, active_required

blog_bp = Blueprint('blog', __name__)


@blog_bp.route('/')
def index():
    """List all blog posts - GLOBAL blog, everyone can read"""
    posts = Post.get_all()
    return render_template('blog/posts.html', posts=posts)


@blog_bp.route('/post/<int:post_id>')
def view_post(post_id):
    """View single blog post"""
    post = Post.get_by_id(post_id)
    if not post:
        flash('Post not found!', 'danger')
        return redirect(url_for('blog.index'))
    
    return render_template('blog/view_post.html', post=post)


@blog_bp.route('/create', methods=['GET', 'POST'])
@login_required
@active_required
def create_post():
    """Create new blog post"""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        
        # Validation
        if not title or not content:
            flash('Title and content are required!', 'danger')
            return render_template('blog/create_post.html')
        
        # Create post
        post_id = Post.create(session['user_id'], title, content)
        
        if post_id:
            flash('Post created successfully!', 'success')
            return redirect(url_for('blog.view_post', post_id=post_id))
        else:
            flash('Failed to create post. Please try again.', 'danger')
    
    return render_template('blog/create_post.html')


@blog_bp.route('/edit/<int:post_id>', methods=['GET', 'POST'])
@login_required
@active_required
def edit_post(post_id):
    """Edit blog post"""
    post = Post.get_by_id(post_id)
    if not post:
        flash('Post not found!', 'danger')
        return redirect(url_for('blog.index'))
    
    # Check if user owns the post
    if post['user_id'] != session['user_id']:
        flash('You do not have permission to edit this post!', 'danger')
        return redirect(url_for('blog.view_post', post_id=post_id))
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        
        # Validation
        if not title or not content:
            flash('Title and content are required!', 'danger')
            return render_template('blog/edit_post.html', post=post)
        
        # Update post
        if Post.update_post(post_id, title, content):
            flash('Post updated successfully!', 'success')
            return redirect(url_for('blog.view_post', post_id=post_id))
        else:
            flash('Failed to update post. Please try again.', 'danger')
    
    return render_template('blog/edit_post.html', post=post)


@blog_bp.route('/delete/<int:post_id>', methods=['POST'])
@login_required
@active_required
def delete_post(post_id):
    """Delete blog post"""
    post = Post.get_by_id(post_id)
    if not post:
        flash('Post not found!', 'danger')
        return redirect(url_for('blog.index'))
    
    # Check if user owns the post or is admin
    user = User.get_by_id(session['user_id'])
    if post['user_id'] != session['user_id'] and user['role'] != 'admin':
        flash('You do not have permission to delete this post!', 'danger')
        return redirect(url_for('blog.view_post', post_id=post_id))
    
    # Delete post
    if Post.delete_post(post_id):
        flash('Post deleted successfully!', 'success')
        return redirect(url_for('blog.index'))
    else:
        flash('Failed to delete post. Please try again.', 'danger')
        return redirect(url_for('blog.view_post', post_id=post_id))


@blog_bp.route('/my-posts')
@login_required
@active_required
def my_posts():
    """View ALL blog posts - GLOBAL"""
    posts = Post.get_all()
    return render_template('blog/my_posts.html', posts=posts)
