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


const a_items = document.getElementsByClassName('answer-like-section')

for (let item of a_items) {
    const like_btn = item.children[0];

    like_btn.addEventListener('click', () => {
        const formData = new FormData();
        formData.append("answer_id", like_btn.dataset.answer)

        const request = new Request('/answer/like', {
            method: 'POST',
            body: formData,
            headers: {
                "X-CSRFToken": getCookie("csrftoken")
            }
        });
        fetch(request)
            .then((response) => response.json())
            .then((data) => {
                let is_maked_right = data.is_maked_right
                if (is_maked_right) {
                    like_btn.classList.replace("btn-success", "btn-outline-success")
                } else {
                    like_btn.classList.replace("btn-outline-success", "btn-success")
                }
            });
    })
}