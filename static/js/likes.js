document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.like-button').forEach(button => {
        button.addEventListener('click', function() {
            const tweetId = this.dataset.tweetId;
            
            fetch(`/tweet/${tweetId}/like`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            })
            .then(response => response.json())
            .then(data => {
                // Update like count
                const countElement = this.querySelector('.like-count');
                countElement.textContent = data.likes;
                
                // Toggle liked class
                if (data.status === 'liked') {
                    this.classList.add('liked');
                } else {
                    this.classList.remove('liked');
                }
            })
            .catch(error => console.error('Error:', error));
        });
    });
});
