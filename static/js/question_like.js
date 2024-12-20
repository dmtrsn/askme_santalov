function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


const items = document.getElementsByClassName('like-section')

for (let item of items) {
    const [raiting_block, buttons_block] = item.children;
    const [raiting, text] = raiting_block.children;
    const [like_btn, dislike_btn] = buttons_block.children;

    for (let btn of buttons_block.children) {
        btn.addEventListener('click', () => {
            const formData = new FormData();
            formData.append("question_id", btn.dataset.question)
            formData.append("raiting_type", btn.dataset.ltype)

            const request = new Request('/question/like', {
                method: 'POST',
                body: formData,
                headers: {
                    "X-CSRFToken": getCookie("csrftoken")
                }
            });
            fetch(request)
                .then((response) => response.json())
                .then((data) => {
                    raiting.innerHTML = data.raiting
                    if(data.is_liked){
                        like_btn.classList.replace("btn-success", "btn-outline-success")
                    } else {
                        like_btn.classList.replace("btn-outline-success", "btn-success")
                    }
                    if(data.is_dislaked){
                        dislike_btn.classList.replace("btn-danger", "btn-outline-danger")
                    } else {
                        dislike_btn.classList.replace("btn-outline-danger", "btn-danger")
                    }
                });
        })
    }
}