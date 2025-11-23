-- =============================================
-- MOI_Operations Database Schema
-- Only operational (OLTP) tables
-- =============================================

SET ANSI_NULLS ON;
SET QUOTED_IDENTIFIER ON;
GO

-- =============================================
-- OPERATIONAL TABLES (dbo schema only)
-- =============================================

CREATE TABLE [dbo].[User] (
    [userId] NVARCHAR(450) NOT NULL,
    [isAnonymous] BIT NOT NULL DEFAULT 0,
    [createdAt] DATETIME2(7) NOT NULL DEFAULT GETUTCDATE(),
    [role] NVARCHAR(50) NOT NULL CHECK ([role] IN ('citizen', 'officer', 'admin')),
    [email] NVARCHAR(256) NULL,
    [phoneNumber] NVARCHAR(20) NULL,
    [hashedDeviceId] NVARCHAR(256) NULL,
    CONSTRAINT [PK_User] PRIMARY KEY CLUSTERED ([userId]),
    CONSTRAINT [CK_User_ContactInfo] CHECK ([isAnonymous] = 1 OR [email] IS NOT NULL OR [phoneNumber] IS NOT NULL)
);
GO

CREATE TABLE [dbo].[Report] (
    [reportId] NVARCHAR(450) NOT NULL,
    [title] NVARCHAR(500) NOT NULL,
    [descriptionText] NVARCHAR(MAX) NOT NULL,
    [locationRaw] NVARCHAR(2048) NULL,
    [status] NVARCHAR(50) NOT NULL DEFAULT 'Submitted'
        CHECK ([status] IN ('Submitted', 'Assigned', 'InProgress', 'Resolved', 'Rejected')),
    [categoryId] NVARCHAR(100) NOT NULL,
    [aiConfidence] FLOAT NULL CHECK ([aiConfidence] >= 0 AND [aiConfidence] <= 1),
    [createdAt] DATETIME2(7) NOT NULL DEFAULT GETUTCDATE(),
    [updatedAt] DATETIME2(7) NOT NULL DEFAULT GETUTCDATE(),
    [userId] NVARCHAR(450) NULL,
    [transcribedVoiceText] NVARCHAR(MAX) NULL,
    CONSTRAINT [PK_Report] PRIMARY KEY CLUSTERED ([reportId]),
    CONSTRAINT [FK_Report_User] FOREIGN KEY ([userId]) REFERENCES [dbo].[User]([userId]) ON DELETE SET NULL
);
GO

CREATE TABLE [dbo].[Attachment] (
    [attachmentId] NVARCHAR(450) NOT NULL,
    [reportId] NVARCHAR(450) NOT NULL,
    [blobStorageUri] NVARCHAR(2048) NOT NULL,
    [mimeType] NVARCHAR(100) NOT NULL,
    [fileType] NVARCHAR(50) NOT NULL CHECK ([fileType] IN ('image', 'video', 'audio')),
    [fileSizeBytes] BIGINT NOT NULL CHECK ([fileSizeBytes] > 0),
    CONSTRAINT [PK_Attachment] PRIMARY KEY CLUSTERED ([attachmentId]),
    CONSTRAINT [FK_Attachment_Report] FOREIGN KEY ([reportId]) REFERENCES [dbo].[Report]([reportId]) ON DELETE CASCADE
);
GO

-- Operational indexes for fast writes
CREATE NONCLUSTERED INDEX [IX_User_Role] ON [dbo].[User] ([role]) INCLUDE ([userId], [isAnonymous]);
CREATE NONCLUSTERED INDEX [IX_User_HashedDeviceId] ON [dbo].[User] ([hashedDeviceId]) WHERE [hashedDeviceId] IS NOT NULL;
CREATE NONCLUSTERED INDEX [IX_Report_Status] ON [dbo].[Report] ([status]) INCLUDE ([reportId], [title], [createdAt]);
CREATE NONCLUSTERED INDEX [IX_Report_CategoryId] ON [dbo].[Report] ([categoryId]) INCLUDE ([reportId], [title], [status]);
CREATE NONCLUSTERED INDEX [IX_Report_UserId] ON [dbo].[Report] ([userId]) INCLUDE ([reportId], [title], [status], [createdAt]) WHERE [userId] IS NOT NULL;
CREATE NONCLUSTERED INDEX [IX_Report_UpdatedAt] ON [dbo].[Report] ([updatedAt] DESC) INCLUDE ([reportId], [status]); -- For ADF
CREATE NONCLUSTERED INDEX [IX_Report_CreatedAt] ON [dbo].[Report] ([createdAt] DESC) INCLUDE ([reportId], [status], [categoryId]);
CREATE NONCLUSTERED INDEX [IX_Attachment_ReportId] ON [dbo].[Attachment] ([reportId]) INCLUDE ([attachmentId], [fileType], [mimeType]);
GO

-- Trigger for operational table
CREATE TRIGGER [dbo].[TR_Report_UpdateTimestamp]
ON [dbo].[Report]
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE [dbo].[Report]
    SET [updatedAt] = GETUTCDATE()
    FROM [dbo].[Report] r
    INNER JOIN inserted i ON r.[reportId] = i.[reportId]
    WHERE r.[updatedAt] = i.[updatedAt];
END;
GO

-- Watermark table for ADF incremental load
CREATE TABLE [dbo].[ETL_Watermark] (
    [TableName] NVARCHAR(100) NOT NULL PRIMARY KEY,
    [LastExtractedValue] DATETIME2(7) NOT NULL,
    [UpdatedAt] DATETIME2(7) NOT NULL DEFAULT GETUTCDATE()
);
GO

-- Initialize watermark
INSERT INTO [dbo].[ETL_Watermark] ([TableName], [LastExtractedValue])
VALUES ('Report', '1900-01-01 00:00:00');
GO

PRINT 'Operations database schema deployed successfully';
GO