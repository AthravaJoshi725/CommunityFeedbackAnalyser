document.getElementById('linkForm').addEventListener('submit', function() {    
    var page2 = document.querySelector('.page2');
    if (page2) {
        page2.style.display = 'block';
        page2.scrollIntoView({ behavior: 'smooth' });
    }
});
// Add comments function as before
function addComment(imgSrc, userName, time, content, like) {
    const commentContainer = document.createElement('div');
    commentContainer.className = 'comment1';

    const container0 = document.createElement('div');
    container0.className = 'container0';

    const container1 = document.createElement('div');
    container1.className = 'container1';

    const container2 = document.createElement('div');
    container2.className = 'container2';

    const container3 = document.createElement('div');
    container3.className = 'container3';

    const img1 = document.createElement('img');
    img1.src = imgSrc;
    img1.id = 'profile-pic';
    img1.width = 25;
    img1.height = 25;

    const userElement = document.createElement('span');
    userElement.className = 'user-name';
    userElement.id = 'username';
    userElement.textContent = userName;

    const timeElement = document.createElement('span');
    timeElement.className = 'comment-time';
    timeElement.id = 'time';
    timeElement.textContent = time;

    container1.appendChild(userElement);
    container1.appendChild(timeElement);
    container0.appendChild(img1);
    container0.appendChild(container1);

    const likeElement = document.createElement('div');
    likeElement.className = 'comment-likes';
    likeElement.id = 'likes';
    likeElement.textContent = like;

    container2.appendChild(container0);
    container2.appendChild(likeElement);

    const contentElement = document.createElement('span');
    contentElement.className = 'comment-content';
    contentElement.id = 'content';
    contentElement.textContent = content;

    container3.appendChild(container2);
    container3.appendChild(contentElement);

    commentContainer.appendChild(container3);

    const container = document.getElementById('comment');
    container.appendChild(commentContainer);
}

// Example usage of addComment
addComment("https://yt3.ggpht.com/D0xTPjbNSSW0MJ2unPYBrn94XGRaRQT5HzGXsIiUlkTkoBS4dJTT4JtOfRBBQ7rR7qJyE3DpSQ=s88-c-k-c0x00ffffff-no-rj", "@angali_bhushan", "1 year ago", "Thank you so much", "56");
