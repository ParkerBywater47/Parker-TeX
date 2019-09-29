# Parker-TeX
My personal project intended to make producing high quality LaTeX documents vastly easier. I've essentially defined my own language which is parsed into LaTeX code. This software is intended for LaTeX users who find LaTeX syntax clunky and unbearable to work with. Let's start with the syntax I've defined. 

## Syntax    
### Packages 
If a user wishes to use packages in their document, they can be added easily as follows. 
    
    packages[package1, package2, ..., packageX]
    
For sake of later reference, I will refer to this as a packages declaration. 

### Environments
To begin and end a new environment the syntax is as follows: 

    begin[environmnet, option1, option2, option3,...]
        stuff inside environment
        more stuff inside environment
    end[]
    
I've also defined a convenient way to use amsmath matrix environments. The syntax is below. The parameter, data, is a comma separated list of the entries of the matrix in a left-to-right, top-to-bottom order. 
    
    begin[matrix, # rows in matrix, # columns in matrix, data] 
    
    end[]
    
### Commands
Commands with no arguments can be used as follows: 

    commandname[] 
    
Commands with multiple arguments can be used similarly:

    commandname[arg1, arg2, ...]

Ideally, commands with no arguments could be treated as a keyword in order to remove the requirement of 
typing '[]' at the end of each command. Implementing this is problematic though for the following reasons. First, I haven't found 
a way read in command defintions from any given package or class. Given that this process isn't automated, somebody (me) would have to manually add commands to a set of keywords as different users request them. Not very efficient. 

Given the way Parker-Tex parses commands, most LaTeX code will come out of the parser untouched. But, as there are a few bits of LaTeX syntax which will be altered upon compilation, Parker-TeX defines a command to circumvent the issue. This command is `littex[]`. The argument passed to this is untouched by the Parker-TeX parser. 

## Various Bug Fixes
### Alignment type environments 
In the amsmath package there are a set of environments which can be described broadly as equation-aligning 
environments. In each of these environments, there is a bug wherein entering a single blank line generates 
a compile error. As a simple example, let's say you needed to align the following equations: 
    
    a + b = c
    c + d = e
    
Your LaTeX code might look something like this: 

    \begin{align*}
        a + b &= c \\
        c + d &= e \\
        
    \end{align*}
    
As you might have guessed, this code does not compile and you'll get a message that looks something like the followiing:  
       
     "Runaway argument?
     a + b &= c \\ c + d &= e \\ 
     ! Paragraph ended before \align* was complete.
     <to be read again> 
        \par 
     l.35"

If the above code is rewritten as below, there is no compile error.

    \begin{align*} 
        a + b &= c \\  
        c + d &= e \\
    \end{align*} 

As you can see, a blank line (which is ignored by the LaTeX compiler in almost every other usage) caused a compile error. This is bad, so I made sure Parker-TeX fixed this. 
