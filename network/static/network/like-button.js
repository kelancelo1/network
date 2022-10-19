document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".like-button").forEach(button => {
        button.onclick = () => {
            fetch(`/post/${button.dataset.postId}`, {
                method: "PUT",
                body: JSON.stringify({ liked: !button.classList.contains("bi-hand-thumbs-up-fill") })
            })
                .then(response => {
                    if (response.ok) {
                        response.json()
                            .then(data => {
                                button.parentElement.querySelector(".like-count").innerHTML = data.like_count
                                if (data.liked) button.classList.replace("bi-hand-thumbs-up", "bi-hand-thumbs-up-fill");
                                else button.classList.replace("bi-hand-thumbs-up-fill", "bi-hand-thumbs-up");
                            })
                    }
                })
        }
    })
})
