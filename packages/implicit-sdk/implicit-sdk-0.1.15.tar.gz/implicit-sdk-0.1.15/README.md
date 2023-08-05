# implicit SDK

Implicit SDK is a new generation of software development tools where you no longer need to write code to build or to consume any server-side APIs (such as SOAP APIs, RESTful API, GraphQL, gRPC, etc..)

All you need to do is just to write any functions in your server-side that needs to be accessiable from the client-side and the implicit SDK generates a JavaScript module that contains the same functions with the same names, parameters documentation, and return value and when the client side developer uses any of these functions, they automatically invoke the corresponding function in the server side and returns a promise that when resolved, it returns the value returned by the function on the server side.

Implicit SDK doesn't only make the work easier for the software developer but also for the machine. Because it automatically manages the communication between clients and the server to enhance performance. For example, if the client script triggered multiple function calls at the same time, it will automatically merge them into one request to the server.


# Supported server-side programming languages

1. PHP
2. Python
3. ~~JavaScript~~ (Under development)


<!--
## Supported Server-Side Languages

- PHP (Old version of the API)
- JavaScript (Under development)
- Python (Under development)

## Server side coding patterns

When writing any server side code, regardless of what kind of application or what is it for, usually it's meant just meant to provide a way for the client-side of an application to perform CRUD operations on one or more data models in a database.

The reflection api provides out-of-the-box classes for such use case and much more.

- Model Gateway: A model gateway in the reflcetion api is a class that allowes you to expose a database entity to the client-side so that clients can interact with data in that model and perform CRUD operations. it also allowes you to manage permissions and define who can do what to what.

## Challenges

| Challenge      | Description      | Suggested Solution|
|----------------|------------------|-------------------|
| Multilinuality | In order to complete the Model Gateway, a user authentication system is required. And that's only available in Python Django. | Start with Python Django only for now |
| Datatype translation | Python datatypes mentioned in docComments need to be traslated into juavascript. | Use a dictionary translation for now |
| Permission Managment | Even with django permission managment we can hardly control what actions each user or group of users is allowed to perform on a particular model and the rule applies to the entire model with all records on it. For exaple, if you want to allow a user to edit only the posts created by them and not anybody else's posts, this is beyond what django's built in permission managment system can do. | Create a patch for Django framework as a custom Permissions model which still depends on the same User and Groups built-in tables | 
| Permission Managment / Record groups | It can be challenging to create a permissions model that allowes us to set permission per a specific set of records, mainly |

-->