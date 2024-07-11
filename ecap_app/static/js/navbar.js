async function getChatList(){
    let chatList = [];
    await getDataFromUrl("/chat_list")
    .then(response => {
        chatList = response.chats;    
    })
    return chatList;
}


function createChatNavbarItem(navbarChatList, userName, userProfilPictureURL, chatID){
    let link = document.createElement("a");
    link.classList.add("dropdown-item");
    link.href= '/messages/' + chatID;
    let div = document.createElement("div");
    div.classList.add("d-flex", "align-items-center");
    let imgDiv = document.createElement("div");
    imgDiv.classList.add("flex-shrink-0");
    let textDiv = document.createElement("div");
    textDiv.classList.add("ms-2");
    let hr = document.createElement("hr");
    hr.classList.add("dropdown-divider");
    imgDiv.innerHTML = '<img class="rounded-circle" src="'+ userProfilPictureURL + '" alt="" style="width: 40px; height: 40px;">';
    textDiv.innerHTML = "<h6 class='fw-normal mb-0'>" + userName + "</h6>";
    div.appendChild(imgDiv);
    div.appendChild(textDiv);
    link.appendChild(div);
    link.appendChild(hr);
    navbarChatList.appendChild(link);
}

async function displayChatList(){
    const navbarChatList = document.getElementById("navbarChatList");
    const chatListItems = document.getElementById("chatListItems");
    chatListItems.innerHTML = "";
    getChatList()
    .then(chatList => {
        chatList[0].forEach(chat => {
            let messageFrom = chat.different_user;
            let profilepicURL = chat.different_user_profilepic_url;
            let chatID = chat.chat_id;
            createChatNavbarItem(chatListItems, messageFrom, profilepicURL, chatID);
        })
    })
}

displayChatList();