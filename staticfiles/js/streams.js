// Define the App ID for Agora, the unique identifier for your Agora project.
const APP_ID = '351d9881f5d3413ba18e08949844fddb'
// Get the channel name and token from the session storage (where they're saved when the user joins).
const CHANNEL = sessionStorage.getItem('room')
const TOKEN = sessionStorage.getItem('token')

// Retrieve the user's unique identifier (UID) and name from the session storage.
let UID = Number(sessionStorage.getItem('UID'))
let NAME = sessionStorage.getItem('name')

// Create an Agora client instance for Real-Time Communication (RTC), using VP8 codec for video.
const client = AgoraRTC.createClient({ mode: 'rtc', codec: 'vp8' })

// Declare variables to store local media tracks (microphone and camera) and remote users.
let localTracks = []
let remoteUsers = {}


// Function to join the channel, create and display the local stream, and subscribe to remote users.
let joinAndDisplayLocalStream = async () => {
    document.getElementById('room-name').innerText = CHANNEL;

    // Set up event listeners for new users joining and leaving the channel.
    client.on('user-published', handleUserJoined);
    client.on('user-left', handleUserLeft);

    try {
        // Attempt to join the Agora channel using the provided App ID, channel, token, and UID.
        await client.join(APP_ID, CHANNEL, TOKEN, UID);
    } catch (error) {
        console.error("Error joining channel:", error);
        window.open('/', '_self'); // Redirect to home if joining fails.
    }

    // Create the local media tracks (audio and video).
    localTracks = await AgoraRTC.createMicrophoneAndCameraTracks();
    let member = await createMember(); // Create a new member for the server.

    // Generate the HTML to display the local video feed.
    let player = `<div class="video-container" id="user-container-${UID}">
                    <div class="username-wrapper"><span class="user-name">${member.name}</span></div>
                    <div class="video-player" id="user-${UID}"></div>
                </div>`;
    document.getElementById('video-streams').insertAdjacentHTML('beforeend', player);

    // Play the local video stream and publish it to the channel.
    localTracks[1].play(`user-${UID}`);
    await client.publish([localTracks[0], localTracks[1]]);

    // Subscribe to existing remote users if any are already in the channel.
    for (let user of client.remoteUsers) {
        console.log("Subscribing to existing user:", user.uid);
        await subscribeToRemoteUser(user);
    }
};


let isProcessing = false;  // Flag to track if the subscription process is already running


// Function to subscribe to a remote user's media (audio and video).
let subscribeToRemoteUser = async (user) => {
    if (isProcessing) {
        console.log("Subscription process is already running, skipping...");
        return;  // Exit if the process is already running
    }

    isProcessing = true;  // Set the flag to indicate that the process is running

    try {
        // Subscribe to the user's video and audio streams.
        await client.subscribe(user, 'video').catch(console.error);
        await client.subscribe(user, 'audio').catch(console.error);

        // If the user is new, create the UI for their video feed.
        let player = document.getElementById(`user-container-${user.uid}`);
        if (!player) {
            let member = await getMember(user); // Fetch remote user information from the server.
            player = `<div class="video-container" id="user-container-${user.uid}">
                        <div class="username-wrapper"><span class="user-name">${member.name}</span></div>
                        <div class="video-player" id="user-${user.uid}"></div>
                    </div>`;
            document.getElementById('video-streams').insertAdjacentHTML('beforeend', player);
        }

        // Play the remote user's video and audio streams if available.
        if (user.videoTrack) {
            user.videoTrack.play(`user-${user.uid}`);
        }

        if (user.audioTrack) {
            user.audioTrack.play();
        }
    } catch (error) {
        console.error("Error subscribing to user:", user.uid, error);
    }

    isProcessing = false;  // Reset the flag after the process is complete
};


// Event handler for when a new user joins the channel.
let handleUserJoined = async (user, mediaType) => {
    remoteUsers[user.uid] = user;
    await subscribeToRemoteUser(user);
};


// Event handler for when a user leaves the channel.
let handleUserLeft = async (user) => {
    delete remoteUsers[user.uid];
    document.getElementById(`user-container-${user.uid}`)?.remove();
};


// Function to leave the channel, stop local media tracks, and redirect to the home page.
let leaveAndRemoveLocalStream = async () => {
    // Stop and close all local media tracks (camera and microphone).
    for (let i = 0; localTracks.length > i; i++) {
        localTracks[i].stop()
        localTracks[i].close()
    }

    // Leave the Agora channel.
    await client.leave()

    // Delete the local user's member information from the server.
    deleteMember()

    // Redirect to the home page after leaving the channel.
    window.open('/', '_self')
}


// Function to toggle the local camera on/off.
let toggleCamera = async (e) => {
    // If the camera is off (muted), unmute it and change the button style.
    if (localTracks[1].muted) {
        await localTracks[1].setMuted(false)
        e.target.style.backgroundColor = '#fff'
    } else {
        // If the camera is on, mute it and change the button style.
        await localTracks[1].setMuted(true)
        e.target.style.backgroundColor = 'rgb(255, 80, 80, 1)'
    }

    // Re-subscribe to remote users after toggling the camera.
    for (let user of client.remoteUsers) {
        console.log("Re-subscribing to user:", user.uid);
        await subscribeToRemoteUser(user);
    }
}


// Function to toggle the local microphone on/off.
let toggleMic = async (e) => {
    // If the microphone is off (muted), unmute it and change the button style.
    if (localTracks[0].muted) {
        await localTracks[0].setMuted(false)
        e.target.style.backgroundColor = '#fff'
    } else {
        // If the microphone is on, mute it and change the button style.
        await localTracks[0].setMuted(true)
        e.target.style.backgroundColor = 'rgb(255, 80, 80, 1)'
    }
}


// Function to create a new member on the server.
let createMember = async () => {
    let response = await fetch('/create_member/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            "X-CSRFToken": getCookie('csrftoken')  // CSRF token for security
        },
        body: JSON.stringify({ 'name': NAME, 'room_name': CHANNEL, 'UID': UID })
    })

    let member = await response.json()
    return member
}


// Function to retrieve member details from the server based on UID.
let getMember = async (user) => {
    let response = await fetch(`/get_member/?UID=${user.uid}&room_name=${CHANNEL}`)
    let member = await response.json()

    return member
}


// Function to delete the member from the server when they leave the channel.
let deleteMember = async () => {
    let response = await fetch('/delete_member/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            "X-CSRFToken": getCookie('csrftoken')  // CSRF token for security
        },
        body: JSON.stringify({ 'name': NAME, 'room_name': CHANNEL, 'UID': UID })
    })

    let member = await response.json()
}


// Function to retrieve member's UID from the server based on username.
let getUidByUsername = async (username) => {
    // Capitalize the first letter of the username for consistency.
    username = username.charAt(0).toUpperCase() + username.slice(1).toLowerCase();

    // Make a request to the server to fetch the UID for the given username and room name.
    let response = await fetch(`/get_uid_by_username/?username=${username}&room_name=${CHANNEL}`);

    // Parse the server's response as JSON.
    let data = await response.json();

    // Check if the server returned an error.
    if (data.error) {
        console.error('Error:', data.error);
        return null; // Return null if an error occurred.
    }

    // Return the UID from the server's response.
    return data.uid;
};


// Variable to track the previous host
let previousHost = null;

// Function to fetch and update the list of participants in the room.
async function updateParticipants() {
    try {
        // Fetch the list of participants for the current room from the server.
        const response = await fetch(`/get_participants/${CHANNEL}/`);
        const data = await response.json();

        if (data.status === "success") {
            const participantsList = document.getElementById("participants-list");

            // Clear the existing participants list from the UI.
            participantsList.innerHTML = "";

            let localUserInRoom = false;
            let currentHost = null; // Track the current host during this update

            // Iterate over the list of participants returned by the server.
            data.participants.forEach(participant => {
                // Check if the local user is in the room by comparing usernames (case-insensitive).
                if (participant.username.toLowerCase() === NAME.toLowerCase()) {
                    localUserInRoom = true;
                }

                // Identify the current host
                if (participant.is_host) {
                    currentHost = participant.username;
                }
                
                // Generate the HTML for each participant.
                const participantItem = `
                    <div class="participant-item">
                        <div class="participant-details">
                            <p class="participant-name">${participant.username}</p>
                            ${participant.is_host ? `<span class="host-label">Host</span>` : ""}
                        </div>

                        <!-- Buttons go on the next line -->
                        ${isHost && !participant.is_host ? `
                            <div class="participant-actions">
                                <button class="host-btn" onclick="changeHost('${participant.username}')">Make Host</button>
                                <button class="remove-btn" onclick="removeParticipant('${participant.username}')">Remove</button>
                            </div>
                        ` : ""}
                    </div>
                `;

                // Add the participant's HTML to the list in the UI.
                participantsList.insertAdjacentHTML("beforeend", participantItem);
            });

            // If the local user is not found in the participants list, leave the channel and clean up.
            if (!localUserInRoom) {
                console.log("Local user is no longer in the participants list. Leaving the channel...");
                await leaveAndRemoveLocalStream();
            }

            // Check if the host has changed
            if (currentHost !== previousHost) {
                console.log(`Host has changed from ${previousHost || "None"} to ${currentHost || "None"}`);
                previousHost = currentHost; // Update the previous host
                checkPendingRequests(); // Call the function when the host changes
            }
        } else {
            // Log any errors returned by the server.
            console.log("Error fetching participants: " + data.message);
        }
    } catch (error) {
        // Log any errors that occur during the fetch operation.
        console.error("Error fetching participants:", error);
    }
}


// Function to change the host of the room
let changeHost = async (name) => {
    try {
        // Capitalize the first letter of the username for consistency
        name = name.charAt(0).toUpperCase() + name.slice(1).toLowerCase();

        // Send a request to the server to update the host
        let response = await fetch('/change_host/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                "X-CSRFToken": getCookie('csrftoken')  // CSRF token for security
            },
            body: JSON.stringify({ 'name': name, 'room_name': CHANNEL })
        });

        // Parse the server's response
        let result = await response.json();

        if (result.error) {
            console.error('Error changing host:', result.error);
            return; // Exit if there was an error
        }

        // Log success message
        console.log(`Host has been successfully changed to ${name}.`);
    } catch (error) {
        // Log any errors that occur during the changeHost process
        console.error('Error while changing host:', error);
    }
};


// Function to delete the member from the server and remove the participant (remote user) from the channel.
let removeParticipant = async (name) => {
    try {
        // Capitalize the first letter of the username for consistency.
        name = name.charAt(0).toUpperCase() + name.slice(1).toLowerCase();

        // Retrieve the UID of the participant from the server using their username and room name.
        let uid = await getUidByUsername(name, CHANNEL);

        if (!uid) {
            console.error('UID not found for the username:', name);
            return; // Exit if the UID cannot be found.
        }

        // Send a request to the server to delete the participant by their username and UID.
        let response = await fetch('/remove_participant_by_name/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                "X-CSRFToken": getCookie('csrftoken')  // CSRF token for security
            },
            body: JSON.stringify({ 'name': name, 'room_name': CHANNEL, 'UID': uid })
        });

        // Parse the server's response.
        let member = await response.json();
        if (member.error) {
            console.error('Error deleting member from server:', member.error);
            return; // Exit if there was an error deleting the member.
        }

        // Get the remote user object from the local `remoteUsers` object using the UID.
        let remoteUser = remoteUsers[uid];

        if (!remoteUser) {
            console.error('Remote user not found in remoteUsers:', uid);
            return; // Exit if the remote user object does not exist.
        }

        // Unsubscribe from the remote user's video and audio streams (if they are active).
        try {
            await client.unsubscribe(remoteUser, 'video').catch((error) => {
                console.error('Error unsubscribing video:', error);
            });
            await client.unsubscribe(remoteUser, 'audio').catch((error) => {
                console.error('Error unsubscribing audio:', error);
            });
        } catch (error) {
            // Log any errors that occur during the unsubscribe process.
            console.error('Error while unsubscribing media streams:', error);
        }

        // Remove the remote user from the `remoteUsers` object.
        delete remoteUsers[uid];

        // Remove the remote user's DOM element from the page (if it exists).
        const userContainer = document.getElementById(`user-container-${uid}`);
        if (userContainer) {
            userContainer.remove();
        }

        // Log a success message indicating that the user has been removed.
        console.log(`${name} (UID: ${uid}) has been successfully removed from the channel and server.`);
    } catch (error) {
        // Log any errors that occur during the removeParticipant process.
        console.error('Error while removing participant:', error);
    }
};


// Helper function to get the CSRF token from cookies (used for secure POST requests)
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') { // Check if the `document.cookie` string exists and is not empty
        const cookies = document.cookie.split(';'); // Split the cookie string into individual cookies
        for (let i = 0; i < cookies.length; i++) { // Loop through all cookies
            const cookie = cookies[i].trim(); // Trim leading and trailing spaces for each cookie
            if (cookie.substring(0, name.length + 1) === (name + '=')) { // Check if the cookie starts with the given name
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1)); // Decode and extract the cookie's value
                break; // Stop searching as we've found the cookie
            }
        }
    }
    return cookieValue; // Return the value of the cookie, or null if not found
}


// Call the function to join the channel and display the local stream.
joinAndDisplayLocalStream()


// Call the updateParticipants function on page load to populate the participants list
updateParticipants(); 

// Periodically update the participants list every 3 seconds
setInterval(updateParticipants, 3000);


// Add event listener to delete the member when the window is about to unload (user leaves the page).
window.addEventListener('beforeunload', deleteMember)

// Add event listeners for the leave, camera, and microphone buttons.
document.getElementById('leave-btn').addEventListener('click', leaveAndRemoveLocalStream)
document.getElementById('camera-btn').addEventListener('click', toggleCamera)
document.getElementById('mic-btn').addEventListener('click', toggleMic)
