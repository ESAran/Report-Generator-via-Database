<a id="readme-top"></a>

<!-- PROJECT LOGO -->

<br />
<div align="center">
  <a href="https://github.com/github_username/repo_name">
    <img src="docs/images/project_logo.png" alt="Logo">
  </a>

<h3 align="center">Report Generator via Database</h3>

<p align="center">
    Automated system for generating and sending PDF statements from integrated data sources. 
    <br />
</p>
</div>

<br>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About the Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#usability">Usability</a>
      <ul>
        <li><a href="#examples-of-generated-results">Examples of Generated Results</a></li>
      </ul>
    </li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->

## About the Project

Automated system for generating capital share statements, integrating data from different sources (Databricks, Excel, etc.) and organizing PDF reports by branch and administrator.  
The project includes modules for file manipulation, email sending, automation of Excel spreadsheet updates, and data management, making the monthly distribution of statements more efficient and secure.

This project was born from the need to optimize an old automation previously done with <b>UiPath</b> and the terminal-based service system.<br><br>
The solution was fully rewritten in <b>Python</b>, leveraging APIs and <b>Databricks</b> integration, providing greater flexibility, scalability, and maintainability.

<div align="center">
<br>
  <p>
    <b>The result was an impressive reduction in processing time:</b><br>
    <span style="font-size:1.2em;color:#217346;">
      <b>From 56 hours (7 business days) down to just 12 minutes</b>
    </span>
    <br>
    <span style="font-size:1.1em;color:#FF3621;">
      Approximately <b>99.64%</b> execution time reduction!
    </span>
  </p>
  <br>
</div>

The workflow is as follows: each branch has a table where managers indicate the accounts that need monthly statements and the administrator responsible for each. A central table consolidates this information via query into a single list. This list is validated and enriched with Databricks data, such as balances and transactions, enabling the generation of statements organized by administrator within each branch.

### Built With

* ![Databricks](https://img.shields.io/badge/Databricks-FF3621?style=for-the-badge&logo=Databricks&logoColor=white)
* ![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
* ![Microsoft Excel](https://img.shields.io/badge/Microsoft_Excel-217346?style=for-the-badge&logo=microsoft-excel&logoColor=white)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- USABILITY -->

## Usability

The system was developed to facilitate and automate the generation of capital share statements, integrating data from multiple sources and organizing PDF reports by branch and administrator.  
Each branch informs in its own tables which accounts require statements and which administrator is responsible.  
A central table gathers this information via query, consolidating everything into a single list, validated and enriched with Databricks data such as balances and transactions.  
From there, statements are automatically generated and organized.

<!-- LICENSE -->
## License

Distributed under the project’s license. See `LICENSE` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

Eduardo Slomp Arán - duarans03@gmail.com  

Project link: [https://github.com/ESAran/Report-Generator-via-Database](https://github.com/ESAran/Report-Generator-via-Database)

<p align="right">(<a href="#readme-top">back to top</a>)</p>
