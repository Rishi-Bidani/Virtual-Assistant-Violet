let loggedin_user = document.getElementById('loggedInUser').innerHTML;

const USERTASKKEY = `${loggedin_user}tasks`;

function addTaskUI() {
    content = `<input type="text" placeholder="Enter time" class="taskInputField" id="taskTimeInput" onkeyup="onEnter(event)" autofocus><br>
                <input type="text" placeholder="Enter task" class="taskInputField" id="taskTitleInput" onkeyup="onEnter(event)">`;

    content += `<button id="addTaskCancelButton" class="taskButton" onclick="cancelTaskUI()"> Cancel </button>
                Press 'Enter' key to save.`;

    document.getElementById('addTaskArea').innerHTML = content;
    document.getElementById('taskArea').style.height = "59%";
}

function cancelTaskUI() {
  content = `<button id="addTaskButton" class="taskButton" onclick="addTaskUI()"> Add </button>`;

  document.getElementById('addTaskArea').innerHTML = content;
  document.getElementById('taskArea').style.height = "70%";
}

function getTasks() {
  let timeInput = document.getElementById('taskTimeInput').value.toUpperCase();
  let taskInput = document.getElementById('taskTitleInput').value.toUpperCase();

  let taskObject = {
    time: timeInput,
    task: taskInput
  };

  addTask(taskObject);
}

function addTask(tasks) {
  if (localStorage.getItem(USERTASKKEY) == null) {
    arrayTasks = [tasks];
    localStorage.setItem(USERTASKKEY, JSON.stringify(arrayTasks));
  }
  else {
    existingTasks = localStorage.getItem(USERTASKKEY);
    existingTasks = JSON.parse(existingTasks);
    existingTasks.push(tasks)

    localStorage.setItem(USERTASKKEY, JSON.stringify(existingTasks));
  }
}

function onEnter(event)
{
  if (event.keyCode == 13) {
    if (document.getElementById('taskTimeInput').value != "" && document.getElementById('taskTitleInput').value != "") {
      getTasks();
      cancelTaskUI();
      updateList();
    }
    else {
      alert("Please enter time and task to save!");
    }
  }
}

function updateList() {
  let taskList = JSON.parse(localStorage.getItem(USERTASKKEY));

  document.getElementById('taskTimeArea').innerHTML = "";
  document.getElementById('taskTitleArea').innerHTML = "";

  for (let i=0; i<taskList.length; i++) {
    let time = taskList[i].time;
    let task = taskList[i].task;

    document.getElementById('taskTimeArea').innerHTML += `<div>${time} </div><br>`;
    document.getElementById('taskTitleArea').innerHTML += `<div id="task${i}">${task}<i class="fa fa-trash" style="float:right; cursor:pointer;" onclick="deleteTask('${i}')"></i></div> <br>`;
  }
}

function loadTasks() {
  if (localStorage.getItem(USERTASKKEY) == null || JSON.parse(localStorage.getItem(USERTASKKEY)).length == 0) {
    document.getElementById('taskTimeArea').innerHTML = "";
    document.getElementById('taskTitleArea').innerHTML = "";
    document.getElementById('addTaskButton').innerHTML = "Create list";
  }
  else {
    updateList();
  }
}

function deleteTask(taskIndex) {
  let taskList = JSON.parse(localStorage.getItem(USERTASKKEY));

  taskList.splice(taskIndex, 1);

  localStorage.setItem(USERTASKKEY, JSON.stringify(taskList));

  loadTasks();
}
