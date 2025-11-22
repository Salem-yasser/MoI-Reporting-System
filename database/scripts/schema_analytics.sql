-- =============================================
-- MOI_Analytics Database Schema
-- Only analytics tables (hot/cold)
-- =============================================

SET ANSI_NULLS ON;
SET QUOTED_IDENTIFIER ON;
GO

-- Create schemas
IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'hot')
    EXEC('CREATE SCHEMA [hot]');
GO

IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'cold')
    EXEC('CREATE SCHEMA [cold]');
GO

-- Enable Query Store for performance tuning
ALTER DATABASE CURRENT SET QUERY_STORE = ON;
GO

-- =============================================
-- FACT TABLES for Analytics
-- =============================================

-- Hot facts: Recent data (last 90 days)
CREATE TABLE [hot].[Fact_Reports] (
    [reportId] NVARCHAR(450) NOT NULL,
    [title] NVARCHAR(500) NOT NULL,
    [descriptionText] NVARCHAR(MAX) NOT NULL,
    [locationRaw] NVARCHAR(2048) NULL,
    [status] NVARCHAR(50) NOT NULL,
    [categoryId] NVARCHAR(100) NOT NULL,
    [aiConfidence] FLOAT NULL,
    [createdAt] DATETIME2(7) NOT NULL,
    [updatedAt] DATETIME2(7) NOT NULL,
    [userId] NVARCHAR(450) NULL,
    [userRole] NVARCHAR(50) NULL,
    [isAnonymous] BIT NULL,
    [attachmentCount] INT NOT NULL DEFAULT 0,
    [transcribedVoiceText] NVARCHAR(MAX) NULL,
    [ExtractedAt] DATETIME2(7) NOT NULL DEFAULT GETUTCDATE(),
    CONSTRAINT [PK_Hot_Fact_Reports] PRIMARY KEY CLUSTERED ([reportId])
);
GO

-- Cold facts: Historical data (older than 90 days)
CREATE TABLE [cold].[Fact_Reports] (
    [reportId] NVARCHAR(450) NOT NULL,
    [title] NVARCHAR(500) NOT NULL,
    [status] NVARCHAR(50) NOT NULL,
    [categoryId] NVARCHAR(100) NOT NULL,
    [createdAt] DATETIME2(7) NOT NULL,
    [updatedAt] DATETIME2(7) NOT NULL,
    [userRole] NVARCHAR(50) NULL,
    [isAnonymous] BIT NULL,
    [attachmentCount] INT NOT NULL DEFAULT 0,
    [aiConfidence] FLOAT NULL,
    [ExtractedAt] DATETIME2(7) NOT NULL DEFAULT GETUTCDATE(),
    CONSTRAINT [PK_Cold_Fact_Reports] PRIMARY KEY CLUSTERED ([reportId])
);
GO

-- Analytics-optimized indexes (columnstore for big data)
CREATE NONCLUSTERED INDEX [IX_Hot_CreatedAt] ON [hot].[Fact_Reports] ([createdAt]) INCLUDE ([status], [categoryId]);
CREATE NONCLUSTERED INDEX [IX_Hot_Status] ON [hot].[Fact_Reports] ([status]) INCLUDE ([categoryId], [createdAt]);
CREATE NONCLUSTERED INDEX [IX_Hot_Category] ON [hot].[Fact_Reports] ([categoryId]) INCLUDE ([status], [createdAt]);
CREATE NONCLUSTERED INDEX [IX_Hot_UserRole] ON [hot].[Fact_Reports] ([userRole]) WHERE [userRole] IS NOT NULL;

CREATE NONCLUSTERED INDEX [IX_Cold_CreatedAt] ON [cold].[Fact_Reports] ([createdAt]) INCLUDE ([status], [categoryId]);
CREATE NONCLUSTERED INDEX [IX_Cold_Status] ON [cold].[Fact_Reports] ([status]);
GO

-- Unified view across hot + cold
CREATE VIEW [dbo].[vw_AllReports] AS
SELECT 
    [reportId], [title], [descriptionText], [locationRaw],
    [status], [categoryId], [aiConfidence],
    [createdAt], [updatedAt], [userId], [userRole],
    [isAnonymous], [attachmentCount], [transcribedVoiceText],
    'Hot' AS [DataTier]
FROM [hot].[Fact_Reports]
UNION ALL
SELECT 
    [reportId], [title], NULL AS [descriptionText], NULL AS [locationRaw],
    [status], [categoryId], [aiConfidence],
    [createdAt], [updatedAt], NULL AS [userId], [userRole],
    [isAnonymous], [attachmentCount], NULL AS [transcribedVoiceText],
    'Cold' AS [DataTier]
FROM [cold].[Fact_Reports];
GO

-- Dashboard-ready aggregation views
CREATE VIEW [dbo].[vw_Dashboard_Summary] AS
SELECT 
    [categoryId],
    [status],
    COUNT(*) AS [ReportCount],
    AVG([aiConfidence]) AS [AvgConfidence],
    MAX([createdAt]) AS [LatestReport]
FROM [dbo].[vw_AllReports]
GROUP BY [categoryId], [status];
GO

PRINT 'Analytics database schema deployed successfully';
GO