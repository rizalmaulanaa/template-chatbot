# Ticketing System Schema

## Tables

### ticket
- id (SERIAL PRIMARY KEY) - Auto-incrementing unique identifier for each ticket
- title (VARCHAR(255)) - Brief summary of the ticket issue or request
- description (TEXT) - Detailed explanation of the ticket
- priority (VARCHAR(255)) - Priority level of the ticket
- status (VARCHAR(255)) - Current status of the ticket

## Data Conventions

### Priority Levels
Valid priority values (case-insensitive):
- **critical** - Urgent issues requiring immediate attention
- **high** - Important issues that should be addressed soon
- **medium** - Standard priority for most tickets
- **low** - Minor issues or requests that can be addressed later

### Status Values
Valid status values (case-insensitive):
- **open** - Newly created ticket, not yet assigned
- **in_progress** - Ticket is currently being worked on
- **pending** - Waiting for external input or information
- **resolved** - Issue has been fixed, awaiting confirmation
- **closed** - Ticket is completed and verified

## Business Logic

**Active tickets**: Tickets with status IN ('open', 'in_progress', 'pending')

**Completed tickets**: Tickets with status IN ('resolved', 'closed')

**High-priority active tickets**: Tickets where priority IN ('critical', 'high') AND status IN ('open', 'in_progress', 'pending')

**Overdue analysis**: Tickets are typically considered based on creation time. Since the schema doesn't include created_at, you may need to inform users if time-based queries are requested.

## Query Best Practices

1. **Use ILIKE for text searches** - PostgreSQL case-insensitive pattern matching
   - Example: `WHERE title ILIKE '%bug%'`

2. **Filter by priority and status** - Always validate against known values
   - Example: `WHERE priority = 'high' AND status = 'open'`

3. **Count tickets by category** - Use GROUP BY for aggregations
   - Example: `GROUP BY status, priority`

4. **Order results meaningfully** - Typical ordering by priority then id
   - Example: `ORDER BY CASE WHEN priority = 'critical' THEN 1 WHEN priority = 'high' THEN 2 WHEN priority = 'medium' THEN 3 ELSE 4 END, id`

## Example Queries

### Find all open critical tickets
```sql
SELECT 
    id,
    title,
    description,
    priority,
    status
FROM ticket
WHERE priority = 'critical'
  AND status = 'open'
ORDER BY id;
```

### Count tickets by status
```sql
SELECT 
    status,
    COUNT(*) as ticket_count
FROM ticket
GROUP BY status
ORDER BY ticket_count DESC;
```

### Search tickets by keyword in title or description
```sql
SELECT 
    id,
    title,
    priority,
    status
FROM ticket
WHERE title ILIKE '%login%'
   OR description ILIKE '%login%'
ORDER BY 
    CASE 
        WHEN priority = 'critical' THEN 1
        WHEN priority = 'high' THEN 2
        WHEN priority = 'medium' THEN 3
        ELSE 4
    END,
    id;
```

### Find all active high-priority tickets
```sql
SELECT 
    id,
    title,
    priority,
    status
FROM ticket
WHERE priority IN ('critical', 'high')
  AND status IN ('open', 'in_progress', 'pending')
ORDER BY 
    CASE 
        WHEN priority = 'critical' THEN 1
        ELSE 2
    END,
    id;
```

### Get tickets grouped by priority and status
```sql
SELECT 
    priority,
    status,
    COUNT(*) as count
FROM ticket
GROUP BY priority, status
ORDER BY 
    CASE 
        WHEN priority = 'critical' THEN 1
        WHEN priority = 'high' THEN 2
        WHEN priority = 'medium' THEN 3
        ELSE 4
    END,
    status;
```

## Notes

- The schema uses VARCHAR for priority and status. Consider using ENUMs or lookup tables in production for better data integrity.
- No timestamp fields are present. Consider adding created_at, updated_at, and resolved_at for better tracking.
- No user/assignee information. Consider adding assigned_to, created_by fields for multi-user environments.
- Text fields (title, description) support full-text search capabilities in PostgreSQL if needed.