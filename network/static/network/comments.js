function CommentsModalBodyandFooter(props) {
    const [state, setState] = React.useState({
        page: [],
        page_num: 0,
        page_count: 0,
        commentBody: ""       
    })

    React.useEffect(() => {
        loadComments(1);
    }, [])

    function loadComments(pageNum) {
        fetch(`/comments/${props.postId}?page=${pageNum}`)
        .then(response => response.json())
        .then(data => {
            setState({
                ...state,
                ...data
            });
            document.querySelector(`#post-${props.postId}-comment-count`).innerHTML = data.comment_count;
        })
    }

    function handleChange(e) {
        setState({
            ...state,
            commentBody: e.target.value
        })
    }

    function handleSubmit(e) {
        e.preventDefault();
        fetch(`/comments/${props.postId}`, {
            method: "POST",
            body: JSON.stringify({ body: state.commentBody })
        })
        .then(response => response.json())
        .then(data => {
            loadComments(1);
            setState({
                ...state,
                commentBody: ""
            })
        })
    }

    return (
        <>                
            <div className="modal-body">
                <div className="row gy-2">
                    {state.page.length 
                    ?   state.page.map(comment => { 
                            return <Comment 
                                author={comment.author}
                                body={comment.body}
                                date_created={comment.date_created}
                                />
                        })
                    :   <div className="col-12">No comments.</div>
                    }
                </div>
                {state.page_count > 1 
                ?   <Pagination 
                        loadComments={loadComments}
                        page_num={state.page_num}
                        page_count={state.page_count}
                    /> 
                :   null
                }
            </div>
            <div className="modal-footer">
                <form 
                    className="flex-grow-1" 
                    onSubmit={handleSubmit}
                >
                    <textarea 
                        id="" 
                        rows="2" 
                        className="form-control mb-2"
                        placeholder="Write a comment..."
                        value={state.commentBody} 
                        onChange={handleChange}></textarea>
                    <input type="submit" value="Comment" className="btn btn-primary btn-sm" />
                </form>
            </div>
        </>
    )
}


function Comment(props) {
    return (
        <div className="col-12">
            <div className="card">
                <div className="card-body">
                    <div className="card-title fw-bold">{props.author}</div>
                    <small className="card-text d-block">{props.body}</small>
                    <small className="card-text text-muted d-block">{props.date_created}</small>
                </div>
            </div >
        </div>
    )
}


function Pagination(props) {
    return (
        <nav>
            <ul className="pagination mt-3 mb-0 justify-content-center">
                {props.page_num > 1
                ?   <>
                    <li className="page-item">
                        <a className="page-link" onClick={() => props.loadComments(1)}>
                            First
                        </a>
                    </li>
                    <li className="page-item">
                        <a className="page-link" onClick={() => props.loadComments(props.page_num - 1)}>
                        Previous
                        </a>
                    </li>
                    </>
                :   null
                }
                    
                <small className="mx-2 align-self-center">
                    Page {props.page_num} of {props.page_count}
                </small>
                    
                {props.page_num < props.page_count
                ?   <>
                        <li className="page-item">
                            <a className="page-link" onClick={() => props.loadComments(props.page_num + 1)}>
                                Next
                            </a>
                        </li>
                        <li className="page-item">
                            <a className="page-link" onClick={() => props.loadComments(props.page_count)}>
                                Last
                            </a>
                        </li>
                    </>
                : null
                }
            </ul>
        </nav>
    )
}


document.querySelectorAll(".comments-button").forEach(button => {
    button.onclick = () => {
        // alert("fuck");
        const rootNode = document.querySelector("#root");
        const root = ReactDOM.createRoot(rootNode);
        root.render(<CommentsModalBodyandFooter postId={button.dataset.postId} />)
    }
})
