document.addEventListener("DOMContentLoaded", () => {

    // When an "Edit post" button is clicked, it will be replaced by a "Cancel" button 
    // and the post body will be replaced by an "edit post body" form prefilled with the
    // original post body. 
    document.querySelectorAll(".edit-post-button").forEach(button => {
        button.onclick = () => {
            const postBody = document.querySelector(`#post-${button.dataset.postId}-body`);
            const editForm = document.querySelector(`#edit-post-body-form-${button.dataset.postId}`);
            button.style.display = "none";
            postBody.style.display = "none";
            editForm.style.display = "block";
            editForm.querySelector("textarea").value = postBody.innerHTML;
            document.querySelector(`#cancel-edit-button-${button.dataset.postId}`).style.display = "block";
        }
    })

    // When a "Cancel" button is clicked, it will be replaced by an "Edit post" button
    // and the "edit post body" form is replaced by the post body.
    document.querySelectorAll(".cancel-edit-button").forEach(button => {
        button.onclick = () => {
            button.style.display = "none";
            document.querySelector(`#edit-post-body-form-${button.dataset.postId}`).style.display = "none";
            document.querySelector(`#post-${button.dataset.postId}-body`).style.display = "block";
            document.querySelector(`#edit-post-button-${button.dataset.postId}`).style.display = "block";
        }
    })

    // When an "edit post body" form is submitted, it will make a PUT request to the server
    // and if the update is a success, change the post body with the textarea's value.
    document.querySelectorAll(".edit-post-body-form").forEach(form => {
        form.onsubmit = (e) => {
            e.preventDefault();
            const postBody = document.querySelector(`#post-${form.dataset.postId}-body`);
            fetch(`/post/${form.dataset.postId}`, {
                method: "PUT",
                body: JSON.stringify({ "body": form.querySelector("textarea").value })
            })
                .then(response => {
                    if (response.ok) {
                        form.style.display = "none";
                        document.querySelector(`#cancel-edit-button-${form.dataset.postId}`).style.display = "none";
                        document.querySelector(`#edit-post-button-${form.dataset.postId}`).style.display = "block";
                        postBody.style.display = "block";
                        postBody.innerHTML = form.querySelector("textarea").value;

                    }
                })
        }
    })
})
