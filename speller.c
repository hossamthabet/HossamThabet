https://submit.cs50.io/check50/9e3ced4f2e711147bbafd33e892753e169ec2053
// Implements a dictionary's functionality
#include <ctype.h>

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>


#include <stdbool.h>

#include "dictionary.h"

// hash table size = 2^16
const int HASHTABLE_SIZE = 65536;
int count = 0;
// Represents a node in a hash table
typedef struct node
{
    char word[LENGTH + 1];
    struct node *next;
}
node;

// Hash table

node *table[HASHTABLE_SIZE];

// Hashes word to a number
unsigned int hash(const char *word)
{
    unsigned int hash = 0;
    for (int i=0, n=strlen(word); i<n; i++)
        hash = (hash << 2) ^ word[i];
    int N = hash % HASHTABLE_SIZE;
    return N;
}
// Returns true if word is in dictionary else false
bool check(const char *word)
{

    // make traverse node equal to the speciefic linked list
    node *trav = table[hash(word)];

    while (trav != NULL)
    {
    if (strcasecmp(word, trav->word) == 0)
    {
        return true;
    }
    trav = trav->next;
    }
        return false;
}

// Loads dictionary into memory, returning true if successful else false
bool load(const char *dictionary)
{
    
    // initialise word
    char *word[LENGTH+1];
    // open the dictionary
    FILE *file = fopen(dictionary, "r");

    // if the file is empty print that to user
    if (file == NULL)
    {
        printf("couldn't open the file\n");
        return false;
    }
    // read strings from the file
    // make loop to store untill reaching the EOF
    while (true)
    {
        // break out when reach the EOF
        if (feof(file))
        {
            break;
        }
        fscanf(file, "%s", word);
        // declare new node
    node *new_node = malloc(sizeof(node));

        // copy the word to the new_node
        if (new_node != NULL)
        {
            strcpy(new_node->word,word);
            // call the hash function to determine the N number
           int N = hash(new_node->word);
           count++;
        // insert the new_node in the table index
        new_node->next = table[N];
        table[N] = new_node;
        }
        else
        {
            unload();
            return false;
        }
    }
    // close dictionary
    fclose(file);
    return true;
}

// Returns number of words in dictionary if loaded else 0 if not yet loaded
unsigned int size(void)
{
    return count;
}

// Unloads dictionary from memory, returning true if successful else false
bool unload(void)
{
    for (int i = 0; i < HASHTABLE_SIZE; i++)
    {
        // set pointer to head of list
        node *cursor = table[i];
    while (cursor != NULL)
    {
        //make temp node to free memory
        node *temp = cursor;
        cursor = cursor->next;
        free(temp);
    }
    free(cursor);
    }
    return true;
}
